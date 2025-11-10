'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './lib/AuthContext';
import Navigation from './components/Navigation';
import TopBar from './components/TopBar';
import AuthModal from './components/AuthModal';
import ProfileSettingsModal from './components/ProfileSettingsModal';

export default function Home() {
  const { user, isLoading } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('scamper');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streaming]);

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);
    setStreaming('');

    setMessages(prev => [...prev, { role: 'user', content: userMessage, model: selectedModel }]);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${API_BASE}/api/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          model: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let assistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const text = line.slice(6);
            if (text && text !== '[DONE]') {
              assistantMessage += text;
              setStreaming(assistantMessage);
            }
          }
        }
      }

      if (assistantMessage) {
        setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage, model: selectedModel }]);
        setStreaming('');
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}. Backend: ${process.env.NEXT_PUBLIC_API_URL}`,
        model: selectedModel
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Navigation Sidebar */}
      <Navigation user={user} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
          title="Chat"
          subtitle="Expert rodeo insights, powered by AI"
        >
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="scamper">Scamper (Fast)</option>
            <option value="gold_buckle">Gold Buckle (Balanced)</option>
            <option value="bodacious">Bodacious (Premium)</option>
          </select>
        </TopBar>

        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="text-center mb-8">
                <h2 className="text-4xl font-bold text-yellow-500 mb-2">Welcome to RodeoAI</h2>
                <p className="text-gray-400">Ask me anything about rodeo training, equipment, or strategy.</p>
              </div>

              <div className="grid grid-cols-2 gap-3 max-w-2xl">
                <button
                  onClick={() => setInput("How can I improve my heading technique?")}
                  className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm"
                >
                  Improve heading technique?
                </button>
                <button
                  onClick={() => setInput("What's the best rope for heeling?")}
                  className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm"
                >
                  Best rope for heeling?
                </button>
                <button
                  onClick={() => setInput("How do I train my horse smarter?")}
                  className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm"
                >
                  Train my horse smarter?
                </button>
                <button
                  onClick={() => setInput("What's the best strategy for NFR?")}
                  className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm"
                >
                  Strategy for NFR?
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg: any, idx: number) => (
                <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center flex-shrink-0">
                      <span className="text-black font-bold text-xs">AI</span>
                    </div>
                  )}
                  <div
                    className={`max-w-lg rounded-lg p-4 ${
                      msg.role === 'user'
                        ? 'bg-yellow-500 text-black'
                        : 'bg-gray-900 text-white'
                    }`}
                  >
                    {msg.content}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-700 rounded flex items-center justify-center flex-shrink-0">
                      <span className="text-white font-bold text-xs">ME</span>
                    </div>
                  )}
                </div>
              ))}

              {streaming && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center flex-shrink-0">
                    <span className="text-black font-bold text-xs">AI</span>
                  </div>
                  <div className="max-w-lg rounded-lg p-4 bg-gray-900">
                    {streaming}
                    <span className="animate-pulse">|</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-6">
          <form onSubmit={handleChat} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about team roping, equipment, training..."
              className="flex-1 bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-700 rounded-lg px-6 py-3 font-semibold text-black"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Modals */}
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </div>
  );
}
