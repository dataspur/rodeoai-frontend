'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from './lib/AuthContext';
import AuthModal from './components/AuthModal';
import ProfileSettingsModal from './components/ProfileSettingsModal';

export default function Home() {
  const { user, logout, isLoading } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('scamper');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
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
      <div className="w-64 bg-black border-r border-gray-800 flex flex-col p-4">
        <button className="w-full py-3 px-4 bg-gray-900 rounded-lg hover:bg-gray-800 mb-4 text-left font-semibold">
          + New Chat
        </button>
        
        <div className="flex-1">
          <h3 className="text-xs font-semibold text-gray-500 mb-3">Today's Conversation</h3>
          {messages.length > 0 && (
            <div className="text-sm text-gray-400 cursor-pointer hover:text-white">
              Chat Session
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="border-b border-gray-800 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
              🐴
            </div>
            <div>
              <h1 className="text-2xl font-bold text-yellow-500">RODEO AI</h1>
              <p className="text-sm text-gray-400">Powered by DataSpur</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
            >
              <option value="scamper">⚡ Scamper (Fast)</option>
              <option value="gold_buckle">🏆 Gold Buckle (Balanced)</option>
              <option value="bodacious">💎 Bodacious (Premium)</option>
            </select>

            {!isLoading && (
              <>
                {user ? (
                  <div className="relative">
                    <button
                      onClick={() => setShowUserMenu(!showUserMenu)}
                      className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded"
                    >
                      <span className="text-sm">👤 {user.username}</span>
                    </button>

                    {showUserMenu && (
                      <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-700 rounded-lg shadow-lg z-10">
                        <button
                          onClick={() => {
                            setShowUserMenu(false);
                            setShowProfileModal(true);
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-800 rounded-t-lg"
                        >
                          ⚙️ Profile Settings
                        </button>
                        <a
                          href={`/profile/${user.username}`}
                          className="block w-full text-left px-4 py-2 hover:bg-gray-800"
                        >
                          👤 View My Profile
                        </a>
                        <button
                          onClick={() => {
                            setShowUserMenu(false);
                            logout();
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-800 rounded-b-lg text-red-400"
                        >
                          🚪 Logout
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => setShowAuthModal(true)}
                    className="bg-yellow-500 hover:bg-yellow-600 text-black px-4 py-2 rounded font-semibold"
                  >
                    Login / Sign Up
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="text-center mb-8">
                <div className="text-6xl mb-4">🐴</div>
                <h2 className="text-4xl font-bold text-yellow-500 mb-2">Welcome to RodeoAI</h2>
                <p className="text-gray-400">Expert rodeo insights, powered by AI.</p>
              </div>
              
              <div className="grid grid-cols-2 gap-3 max-w-2xl">
                <button className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm">
                  Improve heading technique?
                </button>
                <button className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm">
                  Best rope for heeling?
                </button>
                <button className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm">
                  Train my horse smarter?
                </button>
                <button className="p-4 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 text-left text-sm">
                  Strategy for NFR?
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg: any, idx: number) => (
                <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center flex-shrink-0 text-sm">
                      🐴
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
                </div>
              ))}
              
              {streaming && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center flex-shrink-0 text-sm">
                    🐴
                  </div>
                  <div className="max-w-lg rounded-lg p-4 bg-gray-900">
                    {streaming}
                    <span className="animate-pulse">▋</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

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
              ➤
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
