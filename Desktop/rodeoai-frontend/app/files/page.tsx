'use client';

import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import Navigation from '../components/Navigation';
import TopBar from '../components/TopBar';
import AuthModal from '../components/AuthModal';
import ProfileSettingsModal from '../components/ProfileSettingsModal';

export default function FilesPage() {
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [files, setFiles] = useState([
    { id: 1, name: 'Bo - Vaccination Record.pdf', type: 'Veterinary', date: '2025-11-01', size: '245 KB' },
    { id: 2, name: 'Training Log - November.pdf', type: 'Training', date: '2025-11-05', size: '128 KB' },
    { id: 3, name: 'Registration Papers - Bo.pdf', type: 'Registration', date: '2025-10-15', size: '892 KB' },
  ]);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = e.target.files;
    if (uploadedFiles) {
      // Handle file upload logic here
      console.log('Files to upload:', uploadedFiles);
    }
  };

  if (!user) {
    return (
      <div className="flex h-screen bg-black text-white">
        <Navigation user={user} />
        <div className="flex-1 flex flex-col">
          <TopBar
            onOpenAuth={() => setShowAuthModal(true)}
            onOpenProfile={() => setShowProfileModal(true)}
            title="My Files"
            subtitle="Upload and manage your rodeo documents"
          />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">Login Required</h2>
              <p className="text-gray-400 mb-6">Please login to access file management</p>
              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-semibold"
              >
                Login / Sign Up
              </button>
            </div>
          </div>
        </div>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
      </div>
    );
  }

  if (!user.is_pro) {
    return (
      <div className="flex h-screen bg-black text-white">
        <Navigation user={user} />
        <div className="flex-1 flex flex-col">
          <TopBar
            onOpenAuth={() => setShowAuthModal(true)}
            onOpenProfile={() => setShowProfileModal(true)}
            title="My Files"
            subtitle="Upload and manage your rodeo documents"
          />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <h2 className="text-2xl font-bold mb-4">Pro Feature</h2>
              <p className="text-gray-400 mb-6">
                File management and personalized RAG knowledge base is available for Pro members.
                Upgrade to upload veterinary records, registration papers, and training logs.
              </p>
              <button className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-semibold">
                Upgrade to Pro
              </button>
            </div>
          </div>
        </div>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-black text-white">
      <Navigation user={user} />

      <div className="flex-1 flex flex-col">
        <TopBar
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
          title="My Files"
          subtitle="Upload and manage your rodeo documents"
        />

        <div className="flex-1 overflow-y-auto p-6">
          {/* Upload Section */}
          <div className="mb-6">
            <label className="block cursor-pointer">
              <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-yellow-500 transition-colors">
                <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-lg font-semibold mb-2">Click to upload files</p>
                <p className="text-sm text-gray-400">Veterinary records, registration papers, training logs</p>
                <input
                  type="file"
                  multiple
                  onChange={handleUpload}
                  className="hidden"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                />
              </div>
            </label>
          </div>

          {/* File Filters */}
          <div className="mb-6 flex gap-3">
            <button className="px-4 py-2 bg-yellow-500 text-black rounded-lg font-semibold">
              All Files
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg">
              Veterinary
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg">
              Training
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg">
              Registration
            </button>
          </div>

          {/* File List */}
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex items-center justify-between hover:border-gray-700">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-800 rounded flex items-center justify-center">
                    <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold">{file.name}</h3>
                    <p className="text-sm text-gray-400">
                      {file.type} • {file.date} • {file.size}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm">
                    View
                  </button>
                  <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-red-400">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Info Box */}
          <div className="mt-6 bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h3 className="font-semibold mb-2">How it works</h3>
            <p className="text-sm text-gray-400 mb-4">
              Upload your veterinary records, horse registration papers, and training logs.
              The AI will analyze these documents and can answer questions like:
            </p>
            <ul className="text-sm text-gray-400 space-y-2">
              <li>• "When is my horse 'Bo' due for his next vaccination?"</li>
              <li>• "What was Bo's training schedule last month?"</li>
              <li>• "Show me Bo's registration details"</li>
            </ul>
          </div>
        </div>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </div>
  );
}
