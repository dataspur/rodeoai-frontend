// API Configuration
// Change this to your deployed backend URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'  // Local development
    : 'https://your-backend.railway.app';  // Production - CHANGE THIS when you deploy

// API Endpoints
const API = {
    // Chat endpoints
    CHAT: `${API_BASE_URL}/api/chat`,
    CONVERSATIONS: `${API_BASE_URL}/api/conversations`,
    FEEDBACK: `${API_BASE_URL}/api/feedback`,

    // User endpoints
    USERS: `${API_BASE_URL}/api/users`,
    AUTH_GOOGLE: `${API_BASE_URL}/api/auth/google`,
    AUTH_ME: `${API_BASE_URL}/api/auth/me`,

    // Payment endpoints
    SUBSCRIPTION_PLANS: `${API_BASE_URL}/api/subscription/plans`,
    CREATE_PAYMENT_INTENT: `${API_BASE_URL}/api/payments/create-intent`,
    CREATE_SUBSCRIPTION: `${API_BASE_URL}/api/payments/create-subscription`,
    MY_PAYMENTS: `${API_BASE_URL}/api/payments/my-payments`,
    MY_SUBSCRIPTION: `${API_BASE_URL}/api/payments/my-subscription`,

    // Product recognition endpoints (Phase 1)
    RECOGNIZE_PRODUCT: `${API_BASE_URL}/api/recognize-product`,
    PRODUCT_ANALYTICS: `${API_BASE_URL}/api/product-analytics`,

    // Webhook
    STRIPE_WEBHOOK: `${API_BASE_URL}/api/webhooks/stripe`,

    // Health check
    HEALTH: `${API_BASE_URL}/health`,
};

console.log('🚀 RodeoAI Frontend initialized');
console.log('📡 API Base URL:', API_BASE_URL);
