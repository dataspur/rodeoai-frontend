from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import sys
import json
import tempfile

# Import database and models
from database import get_db, init_db
from models import User, Conversation, Message, Feedback, SkillLevel, Payment, Subscription
from auth import create_access_token, get_current_user, get_optional_user, get_or_create_user
from payments import PaymentService, SubscriptionPlan

app = FastAPI()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = None
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized", file=sys.stderr)
    else:
        print("⚠ OPENAI_API_KEY not set", file=sys.stderr)
except Exception as e:
    print(f"Error initializing OpenAI: {e}", file=sys.stderr)

# Pydantic models for API requests
class MessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageModel]
    model: str = "gpt-4o-mini"
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None

class FeedbackRequest(BaseModel):
    message_id: Optional[int] = None
    messageIndex: Optional[int] = None
    feedback: str
    message: str
    timestamp: int
    comment: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Chat"
    model: str = "gpt-4o-mini"

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    skill_level: Optional[SkillLevel] = None
    preferences: Optional[Dict] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized", file=sys.stderr)


@app.get("/")
@limiter.limit("100/minute")
def root(request: Request):
    return {"status": "ok", "service": "RodeoAI Backend"}


@app.get("/health")
@limiter.limit("100/minute")
def health(request: Request):
    return {
        "status": "healthy",
        "openai_configured": client is not None
    }


@app.post("/api/chat")
@limiter.limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint that accepts messages array and streams back responses.
    Saves conversation and messages to database.
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI client not initialized. Please set OPENAI_API_KEY environment variable."
        )

    # Map friendly model names to OpenAI model IDs
    model_mapping = {
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4o": "gpt-4o",
        "o1": "gpt-4o",  # o1 is not available via API yet, fallback to gpt-4o
    }

    model_id = model_mapping.get(chat_request.model, "gpt-4o-mini")

    # Get or create conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_request.conversation_id
        ).first()

    if not conversation:
        # Create new conversation
        conversation = Conversation(
            user_id=chat_request.user_id,
            model=chat_request.model,
            title="New Chat"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Get user's skill level for personalized system message
    skill_level = "all skill levels"
    if chat_request.user_id:
        user = db.query(User).filter(User.id == chat_request.user_id).first()
        if user and user.skill_level:
            skill_level = user.skill_level.value

    # Convert Pydantic models to dicts for OpenAI API
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

    # Add system message for rodeo context with skill level
    system_message = {
        "role": "system",
        "content": f"You are RodeoAI, an expert assistant for team roping, rodeo techniques, equipment, and training. The user's skill level is {skill_level}. Provide helpful, accurate advice tailored to their experience level."
    }
    messages.insert(0, system_message)

    # Save user message to database
    if len(chat_request.messages) > 0:
        last_user_msg = chat_request.messages[-1]
        if last_user_msg.role == "user":
            db_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=last_user_msg.content
            )
            db.add(db_message)
            db.commit()

            # Update conversation title from first user message
            if conversation.title == "New Chat":
                title = last_user_msg.content[:50]
                if len(last_user_msg.content) > 50:
                    title += "..."
                conversation.title = title
                db.commit()

    async def generate():
        """Stream responses from OpenAI and save to database."""
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=True,
                max_tokens=2000,
                temperature=0.7,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Save assistant message to database after streaming completes
            db_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response,
                model=model_id
            )
            db.add(db_message)
            conversation.updated_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg, file=sys.stderr)
            yield error_msg

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"X-Conversation-ID": str(conversation.id)}
    )


@app.post("/api/feedback")
@limiter.limit("60/minute")
async def submit_feedback(
    request: Request,
    feedback_request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Record user feedback for assistant responses."""
    try:
        feedback = Feedback(
            message_id=feedback_request.message_id,
            rating=feedback_request.feedback,
            comment=feedback_request.comment
        )
        db.add(feedback)
        db.commit()
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        print(f"Error saving feedback: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}


@app.get("/api/conversations")
@limiter.limit("60/minute")
async def get_conversations(
    request: Request,
    user_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get list of conversations for a user."""
    query = db.query(Conversation)

    if user_id:
        query = query.filter(Conversation.user_id == user_id)

    query = query.filter(Conversation.is_archived == False)
    query = query.order_by(Conversation.updated_at.desc())
    query = query.limit(limit).offset(offset)

    conversations = query.all()

    return [{
        "id": c.id,
        "title": c.title,
        "model": c.model,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "message_count": len(c.messages)
    } for c in conversations]


@app.get("/api/conversations/{conversation_id}")
@limiter.limit("60/minute")
async def get_conversation(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conversation.id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
        "messages": [{
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "model": m.model,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in conversation.messages]
    }


@app.post("/api/conversations")
@limiter.limit("30/minute")
async def create_conversation(
    request: Request,
    conversation: ConversationCreate,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    db_conversation = Conversation(
        user_id=user_id,
        title=conversation.title,
        model=conversation.model
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return {
        "id": db_conversation.id,
        "title": db_conversation.title,
        "model": db_conversation.model,
        "created_at": db_conversation.created_at.isoformat() if db_conversation.created_at else None
    }


@app.patch("/api/conversations/{conversation_id}")
@limiter.limit("60/minute")
async def update_conversation(
    request: Request,
    conversation_id: int,
    update: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update conversation details."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if update.title is not None:
        conversation.title = update.title
    if update.is_archived is not None:
        conversation.is_archived = update.is_archived

    db.commit()
    return {"status": "success"}


@app.delete("/api/conversations/{conversation_id}")
@limiter.limit("30/minute")
async def delete_conversation(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()
    return {"status": "success"}


@app.get("/api/conversations/search")
@limiter.limit("30/minute")
async def search_conversations(
    request: Request,
    q: str,
    user_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search conversations by content."""
    query = db.query(Conversation).join(Message)

    if user_id:
        query = query.filter(Conversation.user_id == user_id)

    # Search in conversation title and message content
    query = query.filter(
        (Conversation.title.ilike(f"%{q}%")) |
        (Message.content.ilike(f"%{q}%"))
    )

    query = query.order_by(Conversation.updated_at.desc())
    query = query.limit(limit)

    conversations = query.all()

    return [{
        "id": c.id,
        "title": c.title,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None
    } for c in conversations]


@app.get("/api/conversations/{conversation_id}/export/text")
@limiter.limit("20/minute")
async def export_conversation_text(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Export conversation as plain text file."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create text content
    content = f"RodeoAI Conversation: {conversation.title}\n"
    content += f"Date: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S') if conversation.created_at else 'N/A'}\n"
    content += "=" * 80 + "\n\n"

    for msg in conversation.messages:
        role = "You" if msg.role == "user" else "RodeoAI"
        timestamp = msg.created_at.strftime('%H:%M:%S') if msg.created_at else ''
        content += f"[{timestamp}] {role}:\n{msg.content}\n\n"

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    return FileResponse(
        temp_path,
        media_type='text/plain',
        filename=f"rodeoai_chat_{conversation.id}.txt"
    )


@app.get("/api/conversations/{conversation_id}/export/pdf")
@limiter.limit("10/minute")
async def export_conversation_pdf(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Export conversation as PDF file."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
        temp_path = f.name

    # Create PDF
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#d4af37',
        spaceAfter=30
    )
    story.append(Paragraph(f"RodeoAI: {conversation.title}", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    meta_text = f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S') if conversation.created_at else 'N/A'}"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Messages
    user_style = ParagraphStyle(
        'User',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#333333',
        spaceAfter=12
    )
    assistant_style = ParagraphStyle(
        'Assistant',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1a1a1a',
        spaceAfter=12
    )

    for msg in conversation.messages:
        role = "You" if msg.role == "user" else "RodeoAI"
        timestamp = msg.created_at.strftime('%H:%M:%S') if msg.created_at else ''

        header = f"<b>[{timestamp}] {role}:</b>"
        story.append(Paragraph(header, styles['Heading3']))

        style = user_style if msg.role == "user" else assistant_style
        story.append(Paragraph(msg.content.replace('\n', '<br/>'), style))
        story.append(Spacer(1, 0.2*inch))

    doc.build(story)

    return FileResponse(
        temp_path,
        media_type='application/pdf',
        filename=f"rodeoai_chat_{conversation.id}.pdf"
    )


@app.get("/api/users/{user_id}")
@limiter.limit("60/minute")
async def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "skill_level": user.skill_level.value if user.skill_level else None,
        "preferences": json.loads(user.preferences) if user.preferences else {},
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@app.patch("/api/users/{user_id}")
@limiter.limit("30/minute")
async def update_user(
    request: Request,
    user_id: int,
    update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update.full_name is not None:
        user.full_name = update.full_name
    if update.skill_level is not None:
        user.skill_level = update.skill_level
    if update.preferences is not None:
        user.preferences = json.dumps(update.preferences)

    db.commit()
    return {"status": "success"}


# OAuth endpoints
@app.post("/api/auth/google")
@limiter.limit("10/minute")
async def google_auth(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token.
    Frontend should use Google OAuth library to get the token.
    """
    try:
        # Verify Google token (this is a placeholder - in production, verify with Google)
        # For now, we'll accept any token for development
        # In production, use google.oauth2 library to verify the token

        # Mock user data - replace with actual Google token verification
        # from google.oauth2 import id_token
        # from google.auth.transport import requests
        # idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # For development, create a test user
        user = get_or_create_user(
            db=db,
            email="test@example.com",  # Replace with idinfo['email']
            full_name="Test User",      # Replace with idinfo['name']
            oauth_provider="google",
            oauth_id="google_123"       # Replace with idinfo['sub']
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "skill_level": user.skill_level.value if user.skill_level else None
            }
        }

    except Exception as e:
        print(f"OAuth error: {e}", file=sys.stderr)
        raise HTTPException(status_code=401, detail="Invalid authentication")


@app.get("/api/auth/me")
@limiter.limit("60/minute")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "skill_level": current_user.skill_level.value if current_user.skill_level else None,
        "preferences": json.loads(current_user.preferences) if current_user.preferences else {},
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


# Payment endpoints
class PaymentIntentRequest(BaseModel):
    amount: float  # Dollar amount
    description: str
    metadata: Optional[Dict] = None


class SubscriptionRequest(BaseModel):
    plan: str  # "pro" or "premium"
    trial_days: Optional[int] = None


@app.get("/api/subscription/plans")
@limiter.limit("100/minute")
async def get_subscription_plans(request: Request):
    """Get available subscription plans and pricing."""
    return {
        "plans": [
            SubscriptionPlan.FREE,
            SubscriptionPlan.PRO,
            SubscriptionPlan.PREMIUM
        ]
    }


@app.post("/api/payments/create-intent")
@limiter.limit("30/minute")
async def create_payment_intent_endpoint(
    request: Request,
    payment_request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for one-time payments (rodeo entries).
    Returns client_secret for Stripe.js to complete payment.
    """
    # Convert dollar amount to cents
    amount_cents = int(payment_request.amount * 100)

    # Get or create Stripe customer
    if not current_user.stripe_customer_id:
        customer = await PaymentService.create_customer(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": current_user.id}
        )
        current_user.stripe_customer_id = customer.id
        db.commit()

    # Create payment intent
    intent = await PaymentService.create_payment_intent(
        amount=amount_cents,
        description=payment_request.description,
        metadata=payment_request.metadata or {},
        customer_id=current_user.stripe_customer_id
    )

    # Save to database
    payment = Payment(
        user_id=current_user.id,
        stripe_payment_intent_id=intent.id,
        amount=amount_cents,
        status=intent.status,
        description=payment_request.description,
        metadata=json.dumps(payment_request.metadata) if payment_request.metadata else None
    )
    db.add(payment)
    db.commit()

    return {
        "client_secret": intent.client_secret,
        "payment_id": payment.id,
        "amount": amount_cents,
        "currency": "usd"
    }


@app.post("/api/payments/create-subscription")
@limiter.limit("10/minute")
async def create_subscription_endpoint(
    request: Request,
    subscription_request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a subscription for Pro or Premium plan.
    Returns client_secret for payment confirmation.
    """
    # Validate plan
    plan = SubscriptionPlan.get_plan_by_name(subscription_request.plan)
    if plan == SubscriptionPlan.FREE:
        raise HTTPException(status_code=400, detail="Cannot create subscription for free plan")

    # Get or create Stripe customer
    if not current_user.stripe_customer_id:
        customer = await PaymentService.create_customer(
            email=current_user.email,
            name=current_user.full_name,
            metadata={"user_id": current_user.id}
        )
        current_user.stripe_customer_id = customer.id
        db.commit()

    # Create subscription
    stripe_subscription = await PaymentService.create_subscription(
        customer_id=current_user.stripe_customer_id,
        price_id=plan["price_id"],
        trial_period_days=subscription_request.trial_days
    )

    # Save to database
    subscription = Subscription(
        user_id=current_user.id,
        stripe_subscription_id=stripe_subscription.id,
        stripe_customer_id=current_user.stripe_customer_id,
        plan=subscription_request.plan.lower(),
        status=stripe_subscription.status,
        current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
        current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end)
    )
    db.add(subscription)
    db.commit()

    # Extract client secret from payment intent
    client_secret = stripe_subscription.latest_invoice.payment_intent.client_secret

    return {
        "subscription_id": subscription.id,
        "client_secret": client_secret,
        "status": stripe_subscription.status
    }


@app.delete("/api/payments/cancel-subscription/{subscription_id}")
@limiter.limit("10/minute")
async def cancel_subscription_endpoint(
    request: Request,
    subscription_id: int,
    at_period_end: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a subscription (at period end by default)."""
    # Get subscription from database
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Cancel on Stripe
    stripe_subscription = await PaymentService.cancel_subscription(
        subscription.stripe_subscription_id,
        at_period_end=at_period_end
    )

    # Update database
    subscription.status = stripe_subscription.status
    subscription.cancel_at_period_end = at_period_end
    db.commit()

    return {
        "status": "canceled" if not at_period_end else "canceling_at_period_end",
        "period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
    }


@app.get("/api/payments/my-payments")
@limiter.limit("60/minute")
async def get_my_payments(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's payment history."""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()

    return [{
        "id": p.id,
        "amount": p.amount / 100,  # Convert to dollars
        "currency": p.currency,
        "status": p.status,
        "description": p.description,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in payments]


@app.get("/api/payments/my-subscription")
@limiter.limit("60/minute")
async def get_my_subscription(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's active subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"])
    ).first()

    if not subscription:
        return {
            "has_subscription": False,
            "plan": "free"
        }

    plan_details = SubscriptionPlan.get_plan_by_name(subscription.plan)

    return {
        "has_subscription": True,
        "id": subscription.id,
        "plan": subscription.plan,
        "status": subscription.status,
        "price": plan_details.get("price", 0),
        "features": plan_details.get("features", []),
        "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "cancel_at_period_end": subscription.cancel_at_period_end
    }


@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    This endpoint receives payment confirmations and subscription updates.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    # Verify webhook signature
    event = PaymentService.construct_webhook_event(payload, sig_header, webhook_secret)

    # Handle different event types
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object

        # Update payment in database
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent.id
        ).first()

        if payment:
            payment.status = "succeeded"
            db.commit()

            print(f"✓ Payment succeeded: {payment_intent.id}", file=sys.stderr)

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object

        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent.id
        ).first()

        if payment:
            payment.status = "failed"
            db.commit()

            print(f"✗ Payment failed: {payment_intent.id}", file=sys.stderr)

    elif event.type == "customer.subscription.created":
        subscription_obj = event.data.object

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_obj.id
        ).first()

        if subscription:
            subscription.status = subscription_obj.status
            db.commit()

    elif event.type == "customer.subscription.updated":
        subscription_obj = event.data.object

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_obj.id
        ).first()

        if subscription:
            subscription.status = subscription_obj.status
            subscription.current_period_start = datetime.fromtimestamp(subscription_obj.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(subscription_obj.current_period_end)
            db.commit()

    elif event.type == "customer.subscription.deleted":
        subscription_obj = event.data.object

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_obj.id
        ).first()

        if subscription:
            subscription.status = "canceled"
            db.commit()

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    print("Starting RodeoAI Backend on http://0.0.0.0:8001")
    print("Make sure OPENAI_API_KEY is set in your environment")
    print("Database will be initialized on first run")
    uvicorn.run(app, host="0.0.0.0", port=8001)
