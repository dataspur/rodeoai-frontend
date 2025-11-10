'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { getMyProfile, createProfile, updateProfile, ContestantProfile } from '../lib/api';

interface ProfileSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ProfileSettingsModal({ isOpen, onClose }: ProfileSettingsModalProps) {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const [formData, setFormData] = useState({
    instagram: '',
    facebook: '',
    snapchat: '',
    tiktok: '',
    x_twitter: '',
    youtube: '',
    hometown: '',
    events: '',
    bio: '',
  });

  useEffect(() => {
    if (isOpen && token) {
      loadProfile();
    }
  }, [isOpen, token]);

  const loadProfile = async () => {
    if (!token) return;

    setLoading(true);
    try {
      const profile = await getMyProfile(token);
      setHasProfile(true);
      setFormData({
        instagram: profile.instagram || '',
        facebook: profile.facebook || '',
        snapchat: profile.snapchat || '',
        tiktok: profile.tiktok || '',
        x_twitter: profile.x_twitter || '',
        youtube: profile.youtube || '',
        hometown: profile.hometown || '',
        events: profile.events || '',
        bio: profile.bio || '',
      });
    } catch (error) {
      setHasProfile(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setSaving(true);
    try {
      if (hasProfile) {
        await updateProfile(token, formData);
      } else {
        await createProfile(token, formData);
        setHasProfile(true);
      }
      alert('Profile saved successfully!');
      onClose();
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-800">
        <div className="sticky top-0 bg-gray-900 border-b border-gray-800 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-yellow-500">Profile Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading...</div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Social Media Section */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Social Media</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Instagram Handle
                  </label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-700 bg-gray-800 text-gray-400">
                      @
                    </span>
                    <input
                      type="text"
                      name="instagram"
                      value={formData.instagram}
                      onChange={handleChange}
                      placeholder="username"
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-r-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Facebook URL
                  </label>
                  <input
                    type="text"
                    name="facebook"
                    value={formData.facebook}
                    onChange={handleChange}
                    placeholder="https://facebook.com/yourpage"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    X (Twitter) Handle
                  </label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-700 bg-gray-800 text-gray-400">
                      @
                    </span>
                    <input
                      type="text"
                      name="x_twitter"
                      value={formData.x_twitter}
                      onChange={handleChange}
                      placeholder="username"
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-r-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    TikTok Handle
                  </label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-gray-700 bg-gray-800 text-gray-400">
                      @
                    </span>
                    <input
                      type="text"
                      name="tiktok"
                      value={formData.tiktok}
                      onChange={handleChange}
                      placeholder="username"
                      className="flex-1 bg-gray-800 border border-gray-700 rounded-r-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Snapchat Handle
                  </label>
                  <input
                    type="text"
                    name="snapchat"
                    value={formData.snapchat}
                    onChange={handleChange}
                    placeholder="username"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    YouTube Channel
                  </label>
                  <input
                    type="text"
                    name="youtube"
                    value={formData.youtube}
                    onChange={handleChange}
                    placeholder="Channel URL"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>
              </div>
            </div>

            {/* Rodeo Info Section */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Rodeo Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Hometown
                  </label>
                  <input
                    type="text"
                    name="hometown"
                    value={formData.hometown}
                    onChange={handleChange}
                    placeholder="City, State"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Events
                  </label>
                  <input
                    type="text"
                    name="events"
                    value={formData.events}
                    onChange={handleChange}
                    placeholder="e.g., Team Roping (Header), Calf Roping"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleChange}
                    placeholder="Tell people about yourself..."
                    rows={4}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-yellow-500"
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={saving}
                className="flex-1 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-700 rounded-lg px-6 py-3 font-semibold text-black"
              >
                {saving ? 'Saving...' : hasProfile ? 'Update Profile' : 'Create Profile'}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
