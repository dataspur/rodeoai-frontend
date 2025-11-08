"""Payment processing service using Stripe for RodeoAI."""
import os
import stripe
from fastapi import HTTPException
from typing import Dict, Optional
from datetime import datetime

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Subscription price IDs (set these in Stripe Dashboard)
PRICE_IDS = {
    "pro_monthly": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_monthly"),
    "premium_monthly": os.getenv("STRIPE_PREMIUM_PRICE_ID", "price_premium_monthly"),
}


class PaymentService:
    """Service class for handling Stripe payment operations."""

    @staticmethod
    async def create_payment_intent(
        amount: int,  # Amount in cents
        currency: str = "usd",
        description: str = "",
        metadata: Optional[Dict] = None,
        customer_id: Optional[str] = None
    ) -> stripe.PaymentIntent:
        """
        Create a Stripe PaymentIntent for one-time payments (rodeo entries).

        Args:
            amount: Amount in cents (e.g., 15000 for $150.00)
            currency: Currency code (default: usd)
            description: Payment description
            metadata: Additional metadata to attach
            customer_id: Stripe customer ID if user exists

        Returns:
            Stripe PaymentIntent object
        """
        try:
            intent_params = {
                "amount": amount,
                "currency": currency,
                "description": description,
                "metadata": metadata or {},
                "automatic_payment_methods": {"enabled": True},
            }

            if customer_id:
                intent_params["customer"] = customer_id

            intent = stripe.PaymentIntent.create(**intent_params)
            return intent

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Payment intent creation failed: {str(e)}"
            )

    @staticmethod
    async def create_customer(
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> stripe.Customer:
        """
        Create a Stripe customer for a user.

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Stripe Customer object
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Customer creation failed: {str(e)}"
            )

    @staticmethod
    async def create_subscription(
        customer_id: str,
        price_id: str,
        trial_period_days: Optional[int] = None
    ) -> stripe.Subscription:
        """
        Create a subscription for a customer.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the subscription plan
            trial_period_days: Number of days for trial period

        Returns:
            Stripe Subscription object
        """
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
            }

            if trial_period_days:
                subscription_params["trial_period_days"] = trial_period_days

            subscription = stripe.Subscription.create(**subscription_params)
            return subscription

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Subscription creation failed: {str(e)}"
            )

    @staticmethod
    async def cancel_subscription(
        subscription_id: str,
        at_period_end: bool = True
    ) -> stripe.Subscription:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at period end or immediately

        Returns:
            Updated Stripe Subscription object
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)

            return subscription

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Subscription cancellation failed: {str(e)}"
            )

    @staticmethod
    async def get_payment_intent(payment_intent_id: str) -> stripe.PaymentIntent:
        """
        Retrieve a payment intent by ID.

        Args:
            payment_intent_id: Stripe payment intent ID

        Returns:
            Stripe PaymentIntent object
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Payment intent not found: {str(e)}"
            )

    @staticmethod
    async def get_subscription(subscription_id: str) -> stripe.Subscription:
        """
        Retrieve a subscription by ID.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Stripe Subscription object
        """
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Subscription not found: {str(e)}"
            )

    @staticmethod
    def construct_webhook_event(
        payload: bytes,
        sig_header: str,
        webhook_secret: str
    ) -> stripe.Event:
        """
        Construct and verify a Stripe webhook event.

        Args:
            payload: Request body bytes
            sig_header: Stripe signature header
            webhook_secret: Webhook secret from Stripe

        Returns:
            Stripe Event object

        Raises:
            HTTPException: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")


class SubscriptionPlan:
    """Subscription plan definitions."""

    FREE = {
        "name": "Free",
        "price": 0,
        "features": [
            "AI chat assistance",
            "Search rodeos",
            "View rodeo details",
            "Basic rodeo information"
        ]
    }

    PRO = {
        "name": "Pro",
        "price": 9.99,
        "price_id": PRICE_IDS["pro_monthly"],
        "features": [
            "Everything in Free",
            "Automated rodeo entry submission",
            "Location-based rodeo finder",
            "Calendar integration",
            "Entry fee payment processing",
            "Standings & results tracking",
            "Email notifications"
        ]
    }

    PREMIUM = {
        "name": "Premium",
        "price": 19.99,
        "price_id": PRICE_IDS["premium_monthly"],
        "features": [
            "Everything in Pro",
            "Partner matching service",
            "Travel planning & optimization",
            "Performance analytics & insights",
            "Priority support",
            "Advanced AI training recommendations",
            "Equipment recommendations"
        ]
    }

    @classmethod
    def get_plan_by_name(cls, name: str) -> Dict:
        """Get plan details by name."""
        plans = {
            "free": cls.FREE,
            "pro": cls.PRO,
            "premium": cls.PREMIUM
        }
        return plans.get(name.lower(), cls.FREE)
