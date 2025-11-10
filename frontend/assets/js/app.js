// ==================== APP STATE ====================
let currentView = 'chat';
let messages = [];
let currentConversationId = null;
let conversations = [];
let currentUser = null;
let deviceFingerprint = null;

// ==================== FINGERPRINTING ====================
(async () => {
    try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        deviceFingerprint = result.visitorId;
        console.log('🔍 Device fingerprint:', deviceFingerprint.substring(0, 16) + '...');
    } catch (error) {
        console.error('Fingerprinting error:', error);
    }
})();

// ==================== SIDEBAR TOGGLE ====================
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleSidebar');

toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// ==================== NAVIGATION ====================
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const view = item.dataset.view;
        switchView(view);
    });
});

function switchView(view) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === view);
    });

    // Update views
    document.getElementById('chatView').style.display = view === 'chat' ? 'flex' : 'none';
    document.getElementById('predictionsView').classList.toggle('active', view === 'predictions');
    document.getElementById('liveResultsView').classList.toggle('active', view === 'live-results');
    document.getElementById('analyticsView').classList.toggle('active', view === 'analytics');

    // Update title
    const titles = {
        'chat': 'Chat',
        'predictions': 'DataSpur Predictions',
        'live-results': 'Live Results',
        'analytics': 'DataSpur Analytics'
    };
    document.getElementById('pageTitle').textContent = titles[view];

    currentView = view;

    // Initialize views
    if (view === 'predictions') initPredictions();
    if (view === 'live-results') initLiveResults();
    if (view === 'analytics') initAnalytics();
}

// ==================== CHAT ====================
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const messagesArea = document.getElementById('messages');

chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
});

// File upload
const attachBtn = document.getElementById('attachBtn');
const fileInput = document.getElementById('fileInput');
let uploadedFile = null;

attachBtn.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadedFile = file;
        chatInput.placeholder = 'File attached: ' + file.name + ' - Message RodeoAI...';
    }
});

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text && !uploadedFile) return;

    // Add user message
    addMessage(text, 'user');
    messages.push({ role: 'user', content: text });

    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatInput.placeholder = 'Message RodeoAI...';

    // Handle image upload (product recognition)
    if (uploadedFile && uploadedFile.type.startsWith('image/')) {
        await handleProductRecognition(uploadedFile);
        uploadedFile = null;
        fileInput.value = '';
        return;
    }

    uploadedFile = null;
    fileInput.value = '';

    // Disable send button during request
    sendBtn.disabled = true;

    try {
        // Call FastAPI backend
        const requestBody = {
            messages: messages.map(m => ({ role: m.role, content: m.content })),
            model: 'gpt-4o-mini',
            conversation_id: currentConversationId,
            user_id: currentUser?.id || null
        };

        const response = await fetch(API.CHAT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(deviceFingerprint && { 'X-Fingerprint': deviceFingerprint })
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('API error: ' + response.status);
        }

        // Get conversation ID from header
        const conversationIdHeader = response.headers.get('X-Conversation-ID');
        if (conversationIdHeader && !currentConversationId) {
            currentConversationId = parseInt(conversationIdHeader);
            await loadConversations();
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        let messageElement = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            assistantMessage += chunk;

            // Create or update message element
            if (!messageElement) {
                messageElement = addMessage('', 'assistant', true);
            }
            messageElement.querySelector('.message-content').textContent = assistantMessage;
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }

        // Save assistant message to history
        if (assistantMessage) {
            messages.push({ role: 'assistant', content: assistantMessage });
        }

    } catch (error) {
        console.error('Chat error:', error);
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    } finally {
        sendBtn.disabled = false;
    }
}

async function handleProductRecognition(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('include_prices', 'true');
    formData.append('consent_to_fingerprinting', 'true');

    try {
        addMessage('🔍 Analyzing image...', 'assistant');

        const response = await fetch(API.RECOGNIZE_PRODUCT, {
            method: 'POST',
            headers: {
                ...(deviceFingerprint && { 'X-Fingerprint': deviceFingerprint })
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Image recognition failed');
        }

        const result = await response.json();

        // Format the response
        let resultText = '📸 Product Recognition Results:\\n\\n';
        resultText += 'Category: ' + result.category.category + ' (' + Math.round(result.category.confidence) + '% confidence)\\n';
        resultText += 'Brand: ' + result.brand.brand + ' (' + Math.round(result.brand.confidence) + '% confidence)\\n\\n';

        if (result.matches && result.matches.length > 0) {
            resultText += 'Top Match: ' + result.matches[0].brand + ' ' + result.matches[0].model + '\\n';
            resultText += 'Similarity: ' + Math.round(result.matches[0].similarity_score * 100) + '%\\n\\n';

            if (result.matches[0].prices && result.matches[0].prices.length > 0) {
                resultText += '💰 Best Prices:\\n';
                result.matches[0].prices.forEach(price => {
                    resultText += '• ' + price.store_name + ': $' + price.price.toFixed(2) + '\\n';
                });
            }
        }

        addMessage(resultText, 'assistant');
        messages.push({ role: 'assistant', content: resultText });

    } catch (error) {
        console.error('Product recognition error:', error);
        addMessage('Sorry, image recognition failed. Please try again.', 'assistant');
    }
}

function addMessage(text, role, returnElement = false) {
    const message = document.createElement('div');
    message.className = 'message ' + role;

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    message.appendChild(content);
    messagesArea.appendChild(message);
    messagesArea.scrollTop = messagesArea.scrollHeight;

    return returnElement ? message : null;
}

// ==================== PREDICTIONS ====================
async function initPredictions() {
    const grid = document.getElementById('predictionsGrid');
    if (grid.dataset.loaded) return;
    grid.dataset.loaded = 'true';

    grid.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">Predictions coming soon! This feature will show AI-powered rodeo event predictions.</p>';
}

// ==================== LIVE RESULTS ====================
async function initLiveResults() {
    const grid = document.getElementById('resultsGrid');
    if (grid.dataset.loaded) return;
    grid.dataset.loaded = 'true';

    grid.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">Live results coming soon! This feature will show real-time rodeo event scores.</p>';
}

// ==================== ANALYTICS ====================
function initAnalytics() {
    if (document.getElementById('performanceChart').chart) return;

    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
            datasets: [{
                label: 'Events Processed',
                data: [65, 78, 92, 88, 101, 115, 128, 142, 156, 165, 187],
                borderColor: '#d4af37',
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b8b8b' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b8b8b' }
                }
            }
        }
    });

    const accCtx = document.getElementById('accuracyChart').getContext('2d');
    new Chart(accCtx, {
        type: 'bar',
        data: {
            labels: ['Bull Riding', 'Barrel Racing', 'Roping', 'Cutting', 'Bronc'],
            datasets: [{
                label: 'Prediction Accuracy %',
                data: [87, 84, 81, 79, 82],
                backgroundColor: '#d4af37',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b8b8b' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8b8b8b' }
                }
            }
        }
    });
}

// ==================== CONVERSATION MANAGEMENT ====================
const newChatBtn = document.getElementById('newChatBtn');
const chatListEl = document.getElementById('chatList');

newChatBtn.addEventListener('click', createNewConversation);

async function loadConversations() {
    try {
        const url = currentUser
            ? API.CONVERSATIONS + '?user_id=' + currentUser.id
            : API.CONVERSATIONS;

        const response = await fetch(url, {
            headers: {
                ...(deviceFingerprint && { 'X-Fingerprint': deviceFingerprint })
            }
        });

        if (response.ok) {
            conversations = await response.json();
            renderConversationList();
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function renderConversationList() {
    chatListEl.innerHTML = '';

    if (conversations.length === 0) {
        chatListEl.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 16px; font-size: 12px;">No conversations yet</p>';
        return;
    }

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'chat-item' + (conv.id === currentConversationId ? ' active' : '');
        item.innerHTML = '<div class="chat-item-title">' + conv.title + '</div><button class="chat-item-delete" data-id="' + conv.id + '">×</button>';

        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('chat-item-delete')) {
                loadConversation(conv.id);
            }
        });

        const deleteBtn = item.querySelector('.chat-item-delete');
        deleteBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            await deleteConversation(conv.id);
        });

        chatListEl.appendChild(item);
    });
}

async function createNewConversation() {
    currentConversationId = null;
    messages = [];
    messagesArea.innerHTML = '';
    renderConversationList();
}

async function loadConversation(convId) {
    try {
        const response = await fetch(API.CONVERSATIONS + '/' + convId, {
            headers: {
                ...(deviceFingerprint && { 'X-Fingerprint': deviceFingerprint })
            }
        });

        if (!response.ok) throw new Error('Failed to load conversation');

        const conversation = await response.json();
        currentConversationId = convId;
        messages = conversation.messages.map(m => ({ role: m.role, content: m.content }));

        // Render messages
        messagesArea.innerHTML = '';
        conversation.messages.forEach(msg => {
            addMessage(msg.content, msg.role);
        });

        renderConversationList();
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

async function deleteConversation(convId) {
    if (!confirm('Delete this conversation?')) return;

    try {
        const response = await fetch(API.CONVERSATIONS + '/' + convId, {
            method: 'DELETE',
            headers: {
                ...(deviceFingerprint && { 'X-Fingerprint': deviceFingerprint })
            }
        });

        if (response.ok) {
            if (convId === currentConversationId) {
                await createNewConversation();
            }
            await loadConversations();
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
    }
}

// ==================== AUTHENTICATION ====================
const authModal = document.getElementById('authModal');
const closeAuthModal = document.getElementById('closeAuthModal');
const authTabs = document.querySelectorAll('.auth-tab');
const loginFormContainer = document.getElementById('loginForm');
const signupFormContainer = document.getElementById('signupForm');
const loginEmailForm = document.getElementById('loginEmailForm');
const signupEmailForm = document.getElementById('signupEmailForm');
const accountBtn = document.getElementById('accountBtn');

accountBtn.addEventListener('click', () => {
    if (currentUser) {
        if (confirm('Logout?')) {
            logout();
        }
    } else {
        authModal.classList.add('active');
    }
});

closeAuthModal.addEventListener('click', () => {
    authModal.classList.remove('active');
});

authModal.addEventListener('click', (e) => {
    if (e.target === authModal) {
        authModal.classList.remove('active');
    }
});

authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabType = tab.dataset.authTab;
        authTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        if (tabType === 'login') {
            loginFormContainer.classList.add('active');
            signupFormContainer.classList.remove('active');
        } else {
            loginFormContainer.classList.remove('active');
            signupFormContainer.classList.add('active');
        }
    });
});

document.querySelectorAll('[data-switch-to]').forEach(link => {
    link.addEventListener('click', () => {
        const targetTab = link.dataset.switchTo;
        const targetButton = document.querySelector('[data-auth-tab="' + targetTab + '"]');
        if (targetButton) targetButton.click();
    });
});

loginEmailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    alert('Login functionality requires OAuth setup. Coming soon!');
    authModal.classList.remove('active');
});

signupEmailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(signupEmailForm);

    if (formData.get('password') !== formData.get('confirmPassword')) {
        alert('Passwords do not match');
        return;
    }

    alert('Signup functionality requires OAuth setup. Coming soon!');
    authModal.classList.remove('active');
});

function logout() {
    currentUser = null;
    accountBtn.textContent = 'Account';
    localStorage.removeItem('auth_token');
    window.location.reload();
}

// ==================== COOKIE CONSENT ====================
const cookieBanner = document.getElementById('cookieBanner');
const cookieSettings = document.getElementById('cookieSettings');
const acceptAllBtn = document.getElementById('acceptAllCookies');
const rejectOptionalBtn = document.getElementById('rejectOptional');
const customizeLink = document.getElementById('cookieCustomize');
const savePreferencesBtn = document.getElementById('savePreferences');

const consentData = localStorage.getItem('cookie_consent');
let userConsent = consentData ? JSON.parse(consentData) : null;

if (!userConsent) {
    cookieBanner.classList.add('active');
}

customizeLink.addEventListener('click', (e) => {
    e.preventDefault();
    cookieSettings.classList.toggle('active');
});

acceptAllBtn.addEventListener('click', () => {
    const consent = {
        essential: true,
        analytics: true,
        training: true,
        timestamp: Date.now()
    };
    saveConsent(consent);
    cookieBanner.classList.remove('active');
});

rejectOptionalBtn.addEventListener('click', () => {
    const consent = {
        essential: true,
        analytics: false,
        training: false,
        timestamp: Date.now()
    };
    saveConsent(consent);
    cookieBanner.classList.remove('active');
});

savePreferencesBtn.addEventListener('click', () => {
    const consent = {
        essential: true,
        analytics: document.getElementById('analyticsCookies').checked,
        training: document.getElementById('trainingCookies').checked,
        timestamp: Date.now()
    };
    saveConsent(consent);
    cookieBanner.classList.remove('active');
});

function saveConsent(consent) {
    localStorage.setItem('cookie_consent', JSON.stringify(consent));
    userConsent = consent;
    console.log('✅ Cookie consent saved:', consent);
}

// ==================== INITIALIZATION ====================
(async () => {
    console.log('🚀 RodeoAI App initialized');

    // Check backend health
    try {
        const response = await fetch(API.HEALTH);
        if (response.ok) {
            const health = await response.json();
            console.log('✅ Backend connected:', health);
        }
    } catch (error) {
        console.warn('⚠️ Backend not reachable. Make sure to start the FastAPI server.');
    }

    // Load conversations
    await loadConversations();

    // Create first conversation if none exist
    if (conversations.length === 0) {
        await createNewConversation();
    }
})();
