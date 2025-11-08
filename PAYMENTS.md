# RodeoAI Payment System Documentation

## Overview

RodeoAI uses **Stripe** for payment processing, supporting both:
- **One-time payments** - For rodeo entry fees
- **Subscriptions** - For Pro ($9.99/mo) and Premium ($19.99/mo) plans

## Setup

### 1. Get Stripe API Keys

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Go to Dashboard → Developers → API keys
3. Copy your keys:
   - **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - **Secret key** (starts with `sk_test_` or `sk_live_`)

### 2. Create Subscription Products

In Stripe Dashboard → Products:

**Pro Plan:**
1. Click "Add product"
2. Name: "RodeoAI Pro"
3. Description: "Automated rodeo entries, location finder, calendar integration"
4. Pricing: $9.99 USD / month
5. Copy the **Price ID** (starts with `price_`)

**Premium Plan:**
1. Click "Add product"
2. Name: "RodeoAI Premium"
3. Description: "Everything in Pro + partner matching, analytics, priority support"
4. Pricing: $19.99 USD / month
5. Copy the **Price ID**

### 3. Set Up Webhook

1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-domain.com/api/webhooks/stripe`
4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Signing secret** (starts with `whsec_`)

### 4. Configure Environment Variables

```bash
# Stripe Configuration
export STRIPE_SECRET_KEY='sk_test_...'
export STRIPE_PUBLISHABLE_KEY='pk_test_...'
export STRIPE_WEBHOOK_SECRET='whsec_...'

# Price IDs from Step 2
export STRIPE_PRO_PRICE_ID='price_...'
export STRIPE_PREMIUM_PRICE_ID='price_...'
```

## API Endpoints

### Get Subscription Plans
```
GET /api/subscription/plans
```

**Response:**
```json
{
  "plans": [
    {
      "name": "Free",
      "price": 0,
      "features": ["AI chat assistance", "Search rodeos", ...]
    },
    {
      "name": "Pro",
      "price": 9.99,
      "price_id": "price_...",
      "features": ["Everything in Free", "Automated entries", ...]
    },
    {
      "name": "Premium",
      "price": 19.99,
      "price_id": "price_...",
      "features": ["Everything in Pro", "Partner matching", ...]
    }
  ]
}
```

### Create Payment Intent (One-time Payment)
```
POST /api/payments/create-intent
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "amount": 150.00,
  "description": "Fort Worth Rodeo Entry Fee",
  "metadata": {
    "rodeo_id": "123",
    "event": "team_roping_heading"
  }
}
```

**Response:**
```json
{
  "client_secret": "pi_...client_secret_...",
  "payment_id": 1,
  "amount": 15000,
  "currency": "usd"
}
```

### Create Subscription
```
POST /api/payments/create-subscription
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
  "plan": "pro",
  "trial_days": 7
}
```

**Response:**
```json
{
  "subscription_id": 1,
  "client_secret": "seti_...client_secret_...",
  "status": "incomplete"
}
```

### Cancel Subscription
```
DELETE /api/payments/cancel-subscription/{subscription_id}?at_period_end=true
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "status": "canceling_at_period_end",
  "period_end": "2025-12-08T00:00:00"
}
```

### Get My Payments
```
GET /api/payments/my-payments
Authorization: Bearer <jwt_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "amount": 150.00,
    "currency": "usd",
    "status": "succeeded",
    "description": "Fort Worth Rodeo Entry Fee",
    "created_at": "2025-11-08T10:30:00"
  }
]
```

### Get My Subscription
```
GET /api/payments/my-subscription
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "has_subscription": true,
  "id": 1,
  "plan": "pro",
  "status": "active",
  "price": 9.99,
  "features": ["Everything in Free", "Automated entries", ...],
  "current_period_start": "2025-11-08T00:00:00",
  "current_period_end": "2025-12-08T00:00:00",
  "cancel_at_period_end": false
}
```

## Frontend Integration

### 1. Include Stripe.js

Add to your HTML `<head>`:
```html
<script src="https://js.stripe.com/v3/"></script>
```

### 2. Initialize Stripe

```javascript
const stripe = Stripe('pk_test_your_publishable_key');
```

### 3. One-Time Payment Flow

```javascript
async function payForRodeoEntry(rodeoId, amount, description) {
    // Get JWT token from login
    const token = localStorage.getItem('auth_token');

    // Create payment intent
    const response = await fetch(`${API_BASE}/api/payments/create-intent`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            amount: amount,
            description: description,
            metadata: { rodeo_id: rodeoId }
        })
    });

    const { client_secret } = await response.json();

    // Show Stripe payment form
    const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
            card: cardElement,  // Stripe card element
            billing_details: {
                name: userName,
                email: userEmail
            }
        }
    });

    if (error) {
        showToast('Payment failed: ' + error.message);
    } else if (paymentIntent.status === 'succeeded') {
        showToast('Payment successful!');
        // Entry will be automatically submitted via webhook
    }
}
```

### 4. Subscription Flow

```javascript
async function subscribeToPlan(plan) {
    const token = localStorage.getItem('auth_token');

    // Create subscription
    const response = await fetch(`${API_BASE}/api/payments/create-subscription`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            plan: plan,  // "pro" or "premium"
            trial_days: 7  // Optional 7-day trial
        })
    });

    const { client_secret, subscription_id } = await response.json();

    // Confirm payment
    const { error, setupIntent } = await stripe.confirmCardSetup(client_secret, {
        payment_method: {
            card: cardElement,
            billing_details: {
                name: userName,
                email: userEmail
            }
        }
    });

    if (error) {
        showToast('Subscription failed: ' + error.message);
    } else {
        showToast('Subscription activated!');
        // Reload user's subscription status
        loadMySubscription();
    }
}
```

### 5. Create Stripe Card Element

```javascript
// Create card element
const elements = stripe.elements();
const cardElement = elements.create('card', {
    style: {
        base: {
            fontSize: '16px',
            color: '#32325d',
            '::placeholder': {
                color: '#aab7c4'
            }
        }
    }
});

// Mount to DOM
cardElement.mount('#card-element');

// Handle errors
cardElement.on('change', (event) => {
    if (event.error) {
        showToast(event.error.message);
    }
});
```

## Webhook Handling

The `/api/webhooks/stripe` endpoint automatically handles:

1. **payment_intent.succeeded** - Updates payment status to "succeeded"
2. **payment_intent.payment_failed** - Updates payment status to "failed"
3. **customer.subscription.created** - Activates subscription
4. **customer.subscription.updated** - Updates subscription details
5. **customer.subscription.deleted** - Marks subscription as canceled

## Testing

### Test Mode

Use Stripe's test card numbers:
- **Success:** `4242 4242 4242 4242`
- **Decline:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`

Any future expiration date, any 3-digit CVC, any ZIP code.

### Test Webhook Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8001/api/webhooks/stripe

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

## Security Best Practices

1. **Never expose secret keys** - Only use in backend
2. **Always verify webhooks** - Check Stripe signature
3. **Use HTTPS in production** - Required for PCI compliance
4. **Store minimal card data** - Let Stripe handle it
5. **Validate amounts server-side** - Never trust client

## Pricing Structure

### Free Tier
- AI chat assistance
- Search rodeos
- View rodeo details
- Basic rodeo information

### Pro Tier ($9.99/month)
- Everything in Free
- Automated rodeo entry submission
- Location-based rodeo finder
- Calendar integration
- Entry fee payment processing
- Standings & results tracking
- Email notifications

### Premium Tier ($19.99/month)
- Everything in Pro
- Partner matching service
- Travel planning & optimization
- Performance analytics & insights
- Priority support
- Advanced AI training recommendations
- Equipment recommendations

## Production Checklist

Before going live:

- [ ] Switch to live API keys (remove `_test_`)
- [ ] Update webhook URL to production domain
- [ ] Test all payment flows end-to-end
- [ ] Set up proper error monitoring
- [ ] Configure email receipts in Stripe
- [ ] Add terms of service and privacy policy
- [ ] Implement refund policy
- [ ] Set up fraud detection rules
- [ ] Enable 3D Secure for cards
- [ ] Test subscription renewals
- [ ] Test failed payment handling
- [ ] Set up billing dispute process

## Support & Troubleshooting

### Common Issues

**"No such customer"**
- User doesn't have Stripe customer ID yet
- Creating payment intent will auto-create customer

**"Payment intent already succeeded"**
- User trying to pay twice
- Check payment status before creating new intent

**"Webhook signature verification failed"**
- Wrong webhook secret
- Check `STRIPE_WEBHOOK_SECRET` environment variable

**"Subscription not found"**
- User trying to access someone else's subscription
- Endpoint properly checks user_id match

### Getting Help

- Stripe Dashboard → Help
- Stripe docs: [stripe.com/docs](https://stripe.com/docs)
- RodeoAI support: support@rodeoai.com

## Example: Complete Payment Flow

```
User Journey: Subscribe to Pro Plan

1. User clicks "Upgrade to Pro" → $9.99/mo

2. Frontend shows Stripe card form
   - Card number, expiry, CVC, ZIP

3. User enters card details

4. Frontend calls:
   POST /api/payments/create-subscription
   { "plan": "pro", "trial_days": 7 }

5. Backend:
   - Creates/gets Stripe customer
   - Creates Stripe subscription
   - Saves to database
   - Returns client_secret

6. Frontend confirms payment with Stripe.js:
   stripe.confirmCardSetup(client_secret, ...)

7. Stripe processes payment

8. Webhook fires: customer.subscription.created

9. Backend updates subscription status to "active"

10. User now has Pro access!

11. Future: Stripe auto-charges monthly
    Webhooks keep database in sync
```

---

**Ready to accept payments!** 💳🤠
