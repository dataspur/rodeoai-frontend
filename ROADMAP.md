# RodeoAI - Advanced Features Roadmap

## Current Status

### ❌ Location Services
**Status:** NOT integrated yet

**What we have:**
- Basic URL detection (localhost vs production)

**What's needed:**
- Geolocation API integration
- Nearby rodeo finder
- Venue/arena locator
- Travel distance calculator

---

### ❌ MCP Integration (ProRodeo.org & NexGenRodeo.com)
**Status:** NOT integrated yet

**What this would enable:**
- Automated rodeo entry submission
- Real-time rodeo schedule fetching
- Results tracking
- Standings updates
- Entry fee payment automation

---

### ❌ Payment Processing
**Status:** NOT integrated yet

**What's needed:**
- Payment gateway integration (Stripe/PayPal/Square)
- Subscription management
- Rodeo entry fee payments
- Premium features billing

---

## Implementation Roadmap

## 1. LOCATION SERVICES 📍

### Phase 1: Basic Geolocation
Add browser geolocation to find user's current location.

**Frontend Changes:**
```javascript
// Add to public/index.html
let userLocation = null;

async function getUserLocation() {
    if (!navigator.geolocation) {
        showToast('Geolocation not supported');
        return null;
    }

    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                resolve(userLocation);
            },
            (error) => reject(error),
            { enableHighAccuracy: true, timeout: 5000 }
        );
    });
}
```

**Backend Changes:**
```python
# Add to models.py
class Rodeo(Base):
    __tablename__ = "rodeos"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    venue = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    entry_fee = Column(Float)
    prize_pool = Column(Float)
    sanctioning_body = Column(String(100))  # PRCA, WPRA, etc.

# Add to main.py
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 3959  # Earth radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@app.get("/api/rodeos/nearby")
async def get_nearby_rodeos(
    latitude: float,
    longitude: float,
    radius_miles: int = 100,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Find rodeos within specified radius of user location."""
    rodeos = db.query(Rodeo).all()

    nearby = []
    for rodeo in rodeos:
        if rodeo.latitude and rodeo.longitude:
            distance = calculate_distance(
                latitude, longitude,
                rodeo.latitude, rodeo.longitude
            )
            if distance <= radius_miles:
                nearby.append({
                    **rodeo.__dict__,
                    "distance_miles": round(distance, 1)
                })

    nearby.sort(key=lambda x: x['distance_miles'])
    return nearby[:limit]
```

**New Dependencies:**
```txt
# Add to requirements.txt
geopy==2.4.1  # Geocoding support
```

---

## 2. MCP INTEGRATION 🔌

### What is MCP?
Model Context Protocol (MCP) allows AI assistants to securely connect to external data sources and APIs. Perfect for integrating with ProRodeo.org and NexGenRodeo.com!

### Phase 1: Create MCP Servers

**Option A: MCP Server for ProRodeo.org**
```python
# Create: Desktop/rodeoai-backend/mcp_prorodeo.py

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import requests
from bs4 import BeautifulSoup
import logging

# Initialize MCP server
server = Server("prorodeo-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available ProRodeo.org tools."""
    return [
        types.Tool(
            name="search_rodeos",
            description="Search for upcoming PRCA rodeos",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "State abbreviation (TX, OK, etc.)"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "event_type": {"type": "string", "description": "Event type (team_roping, etc.)"}
                }
            }
        ),
        types.Tool(
            name="get_rodeo_details",
            description="Get detailed information about a specific rodeo",
            inputSchema={
                "type": "object",
                "properties": {
                    "rodeo_id": {"type": "string", "description": "ProRodeo.org rodeo ID"}
                },
                "required": ["rodeo_id"]
            }
        ),
        types.Tool(
            name="get_standings",
            description="Get current PRCA standings",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {"type": "string", "description": "Event type"},
                    "year": {"type": "integer", "description": "Year"}
                }
            }
        ),
        types.Tool(
            name="submit_entry",
            description="Submit entry to a PRCA rodeo (requires credentials)",
            inputSchema={
                "type": "object",
                "properties": {
                    "rodeo_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "event": {"type": "string"},
                    "partner_id": {"type": "string", "description": "For team events"}
                },
                "required": ["rodeo_id", "user_id", "event"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool execution."""

    if name == "search_rodeos":
        # Scrape or use ProRodeo.org API
        rodeos = await search_prorodeo_rodeos(
            state=arguments.get("state"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            event_type=arguments.get("event_type")
        )
        return [types.TextContent(
            type="text",
            text=f"Found {len(rodeos)} rodeos:\n" + "\n".join([
                f"- {r['name']} in {r['city']}, {r['state']} ({r['date']})"
                for r in rodeos
            ])
        )]

    elif name == "get_rodeo_details":
        details = await get_prorodeo_details(arguments["rodeo_id"])
        return [types.TextContent(
            type="text",
            text=f"Rodeo: {details['name']}\n"
                 f"Location: {details['city']}, {details['state']}\n"
                 f"Dates: {details['dates']}\n"
                 f"Entry Fee: ${details['entry_fee']}\n"
                 f"Added Money: ${details['added_money']}\n"
                 f"Contact: {details['contact']}"
        )]

    elif name == "get_standings":
        standings = await get_prca_standings(
            event=arguments.get("event"),
            year=arguments.get("year")
        )
        return [types.TextContent(
            type="text",
            text="PRCA Standings:\n" + "\n".join([
                f"{i+1}. {s['name']}: ${s['earnings']:,}"
                for i, s in enumerate(standings[:20])
            ])
        )]

    elif name == "submit_entry":
        # This would require ProRodeo.org login credentials
        result = await submit_prorodeo_entry(
            rodeo_id=arguments["rodeo_id"],
            user_id=arguments["user_id"],
            event=arguments["event"],
            partner_id=arguments.get("partner_id")
        )
        return [types.TextContent(
            type="text",
            text=f"Entry submitted successfully!\n"
                 f"Confirmation: {result['confirmation_number']}\n"
                 f"Entry Fee: ${result['entry_fee']}\n"
                 f"Status: {result['status']}"
        )]

    raise ValueError(f"Unknown tool: {name}")


async def search_prorodeo_rodeos(state, start_date, end_date, event_type):
    """Scrape or API call to ProRodeo.org."""
    # Implementation depends on ProRodeo.org's structure
    # Could use web scraping or official API if available

    # Example with web scraping:
    url = "https://prorodeo.com/rodeos"
    params = {
        "state": state,
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse rodeo listings
    rodeos = []
    # ... parsing logic ...

    return rodeos


async def submit_prorodeo_entry(rodeo_id, user_id, event, partner_id=None):
    """Submit automated entry to ProRodeo.org."""
    # This would use Selenium or Playwright for browser automation
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Login to ProRodeo.org
        await page.goto("https://prorodeo.com/login")
        # ... login logic using stored credentials ...

        # Navigate to entry form
        await page.goto(f"https://prorodeo.com/rodeos/{rodeo_id}/enter")

        # Fill out entry form
        await page.fill("#event", event)
        if partner_id:
            await page.fill("#partner", partner_id)

        # Submit
        await page.click("#submit-entry")

        # Get confirmation
        confirmation = await page.text_content("#confirmation-number")

        await browser.close()

        return {
            "confirmation_number": confirmation,
            "entry_fee": 150.00,  # Would get from page
            "status": "confirmed"
        }


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="prorodeo-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Similar MCP Server for NexGenRodeo.com:**
```python
# Create: Desktop/rodeoai-backend/mcp_nexgen.py
# Similar structure but adapted for NexGenRodeo.com's API/structure
```

### Phase 2: Connect MCP to RodeoAI

**Update main.py to use MCP:**
```python
# Add to main.py
import subprocess
import json

async def call_mcp_tool(server: str, tool: str, arguments: dict):
    """Call MCP server tool and return result."""
    mcp_script = f"Desktop/rodeoai-backend/mcp_{server}.py"

    # Start MCP server process
    process = subprocess.Popen(
        ["python", mcp_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Send tool call request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": arguments
        }
    }

    process.stdin.write(json.dumps(request).encode())
    process.stdin.flush()

    # Get response
    response = process.stdout.readline().decode()
    return json.loads(response)


@app.post("/api/rodeos/search")
async def search_rodeos_via_mcp(
    state: str = None,
    start_date: str = None,
    source: str = "prorodeo"  # or "nexgen"
):
    """Search rodeos using MCP integration."""
    result = await call_mcp_tool(
        server=source,
        tool="search_rodeos",
        arguments={
            "state": state,
            "start_date": start_date
        }
    )
    return result
```

**New Dependencies for MCP:**
```txt
# Add to requirements.txt
mcp==0.9.0
playwright==1.40.0
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.15.2  # Alternative to Playwright
```

---

## 3. PAYMENT PROCESSING 💳

### Phase 1: Stripe Integration

**Backend Setup:**
```python
# Add to requirements.txt
stripe==7.0.0

# Create: Desktop/rodeoai-backend/payments.py
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class PaymentService:
    @staticmethod
    async def create_payment_intent(
        amount: int,  # Amount in cents
        currency: str = "usd",
        description: str = "",
        metadata: dict = None
    ):
        """Create a Stripe PaymentIntent."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description=description,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            return intent
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def create_subscription(
        customer_id: str,
        price_id: str
    ):
        """Create a subscription for premium features."""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}]
        )
        return subscription

    @staticmethod
    async def create_customer(email: str, name: str):
        """Create a Stripe customer."""
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        return customer


# Add to models.py
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_payment_intent_id = Column(String(255))
    amount = Column(Integer)  # Amount in cents
    currency = Column(String(3), default="usd")
    status = Column(String(50))  # succeeded, pending, failed
    description = Column(Text)
    rodeo_id = Column(Integer, ForeignKey("rodeos.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="payments")
    rodeo = relationship("Rodeo", backref="payments")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_subscription_id = Column(String(255))
    stripe_customer_id = Column(String(255))
    plan = Column(String(50))  # basic, pro, premium
    status = Column(String(50))  # active, canceled, past_due
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="subscriptions")


# Add to main.py
from payments import PaymentService

@app.post("/api/payments/create-intent")
async def create_payment_intent(
    amount: float,  # Dollar amount
    description: str,
    rodeo_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for rodeo entry or subscription."""
    amount_cents = int(amount * 100)

    intent = await PaymentService.create_payment_intent(
        amount=amount_cents,
        description=description,
        metadata={
            "user_id": current_user.id,
            "rodeo_id": rodeo_id
        }
    )

    # Save to database
    payment = Payment(
        user_id=current_user.id,
        stripe_payment_intent_id=intent.id,
        amount=amount_cents,
        status=intent.status,
        description=description,
        rodeo_id=rodeo_id
    )
    db.add(payment)
    db.commit()

    return {
        "client_secret": intent.client_secret,
        "payment_id": payment.id
    }


@app.post("/api/payments/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object

        # Update payment in database
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent.id
        ).first()

        if payment:
            payment.status = "succeeded"

            # If this was a rodeo entry payment, submit the entry
            if payment.rodeo_id:
                # Trigger MCP automated entry submission
                await submit_rodeo_entry_after_payment(
                    user_id=payment.user_id,
                    rodeo_id=payment.rodeo_id,
                    db=db
                )

            db.commit()

    elif event.type == "customer.subscription.created":
        subscription = event.data.object
        # Handle new subscription

    return {"status": "success"}


async def submit_rodeo_entry_after_payment(user_id, rodeo_id, db):
    """Automatically submit rodeo entry after payment succeeds."""
    user = db.query(User).filter(User.id == user_id).first()
    rodeo = db.query(Rodeo).filter(Rodeo.id == rodeo_id).first()

    # Call MCP to submit entry
    result = await call_mcp_tool(
        server="prorodeo" if rodeo.sanctioning_body == "PRCA" else "nexgen",
        tool="submit_entry",
        arguments={
            "rodeo_id": rodeo.external_id,
            "user_id": user.prca_number,  # Add this field to User model
            "event": "team_roping_heading"  # Get from user preferences
        }
    )

    return result
```

**Frontend Setup:**
```html
<!-- Add to public/index.html -->
<script src="https://js.stripe.com/v3/"></script>

<script>
// Initialize Stripe
const stripe = Stripe('your_publishable_key');

async function payForRodeoEntry(rodeoId, amount, description) {
    // Create payment intent
    const response = await fetch(`${API_BASE}/api/payments/create-intent`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify({
            amount: amount,
            description: description,
            rodeo_id: rodeoId
        })
    });

    const { client_secret } = await response.json();

    // Show Stripe payment form
    const { error } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
            card: cardElement,
            billing_details: {
                name: userName,
                email: userEmail
            }
        }
    });

    if (error) {
        showToast('Payment failed: ' + error.message);
    } else {
        showToast('Payment successful! Entry submitted automatically.');
    }
}
</script>
```

---

## COMPLETE WORKFLOW EXAMPLE

### User Story: Enter a Rodeo with Automation

1. **User:** "Show me upcoming team roping rodeos near me"
   - Frontend gets user location via geolocation
   - Backend calls MCP ProRodeo server to search
   - Returns list with distances

2. **User:** "Tell me more about the Fort Worth rodeo"
   - Backend calls MCP to get rodeo details
   - Shows entry fees, dates, added money

3. **User:** "Enter me in the Fort Worth rodeo"
   - Frontend shows Stripe payment form
   - User enters card details
   - Payment processes through Stripe
   - Webhook confirms payment
   - Backend automatically calls MCP to submit entry to ProRodeo.org
   - Entry confirmation sent to user

4. **User:** "What are my upcoming rodeos?"
   - Shows all paid/entered rodeos from database
   - Can export to calendar

---

## ENVIRONMENT VARIABLES NEEDED

```bash
# Payment
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ProRodeo.org credentials (for automated entry)
PRORODEO_USERNAME=your_prca_number
PRORODEO_PASSWORD=your_password

# NexGen credentials
NEXGEN_USERNAME=your_username
NEXGEN_PASSWORD=your_password
```

---

## PRICING STRUCTURE

### Free Tier
- AI chat assistance
- Search rodeos
- View rodeo details

### Pro Tier ($9.99/month)
- Automated rodeo entry submission
- Location-based rodeo finder
- Calendar integration
- Entry fee payment processing
- Standing/results tracking

### Premium Tier ($19.99/month)
- Everything in Pro
- Partner matching
- Travel planning
- Performance analytics
- Priority support

---

## NEXT STEPS

1. **Phase 1: Location Services** (1-2 weeks)
   - Add geolocation to frontend
   - Create Rodeo model
   - Implement nearby search

2. **Phase 2: MCP Integration** (2-3 weeks)
   - Build ProRodeo.org MCP server
   - Build NexGenRodeo.com MCP server
   - Connect to main application

3. **Phase 3: Payment Processing** (1-2 weeks)
   - Set up Stripe account
   - Implement payment endpoints
   - Add subscription management

4. **Phase 4: Full Automation** (1 week)
   - Connect payments to MCP entry submission
   - Add confirmation emails
   - Build user dashboard

**Total Timeline: 5-8 weeks**

---

Would you like me to start implementing any of these features?
