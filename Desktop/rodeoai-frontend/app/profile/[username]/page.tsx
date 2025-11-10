'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getPublicProfile, PublicProfile } from '../../lib/api';

export default function PublicProfilePage() {
  const params = useParams();
  const router = useRouter();
  const username = params.username as string;
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (username) {
      loadProfile();
    }
  }, [username]);

  const loadProfile = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getPublicProfile(username);
      setProfile(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSocialUrl = (platform: string, handle?: string) => {
    if (!handle) return null;

    switch (platform) {
      case 'instagram':
        return `https://instagram.com/${handle}`;
      case 'facebook':
        return handle.startsWith('http') ? handle : `https://facebook.com/${handle}`;
      case 'x_twitter':
        return `https://x.com/${handle}`;
      case 'tiktok':
        return `https://tiktok.com/@${handle}`;
      case 'snapchat':
        return `https://snapchat.com/add/${handle}`;
      case 'youtube':
        return handle.startsWith('http') ? handle : `https://youtube.com/${handle}`;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h1 className="text-2xl font-bold mb-2">Profile Not Found</h1>
          <p className="text-gray-400 mb-6">{error || 'This contestant profile does not exist.'}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-yellow-500 hover:bg-yellow-600 rounded-lg px-6 py-3 font-semibold text-black"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 p-6">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
            <span className="font-bold text-black text-lg">R</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-yellow-500">RODEO AI</h1>
            <p className="text-sm text-gray-400">Contestant Profile</p>
          </div>
        </div>
      </div>

      {/* Profile Content */}
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-yellow-500 to-orange-500 h-32"></div>

          <div className="p-8">
            {/* Profile Info */}
            <div className="flex items-start gap-6 -mt-16 mb-6">
              <div className="w-24 h-24 bg-gray-900 border-4 border-gray-900 rounded-full flex items-center justify-center">
                <svg className="w-16 h-16 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div className="flex-1 mt-16">
                <div className="flex items-center gap-3">
                  <h2 className="text-3xl font-bold">{profile.full_name || profile.username}</h2>
                  {profile.profile?.is_verified && (
                    <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">
                      ✓ Verified
                    </span>
                  )}
                </div>
                <p className="text-gray-400">@{profile.username}</p>
              </div>
            </div>

            {/* Rodeo Info */}
            {profile.profile && (
              <>
                {(profile.profile.hometown || profile.profile.events) && (
                  <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {profile.profile.hometown && (
                      <div>
                        <p className="text-sm text-gray-400">Hometown</p>
                        <p className="font-semibold">{profile.profile.hometown}</p>
                      </div>
                    )}
                    {profile.profile.events && (
                      <div>
                        <p className="text-sm text-gray-400">Events</p>
                        <p className="font-semibold">{profile.profile.events}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Bio */}
                {profile.profile.bio && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">About</h3>
                    <p className="text-gray-300 whitespace-pre-wrap">{profile.profile.bio}</p>
                  </div>
                )}

                {/* Social Links */}
                <div className="border-t border-gray-800 pt-6">
                  <h3 className="text-lg font-semibold mb-4">Follow {profile.full_name || profile.username}</h3>
                  <div className="flex flex-wrap gap-3">
                    {profile.profile.instagram && (
                      <a
                        href={getSocialUrl('instagram', profile.profile.instagram) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg px-4 py-2 font-semibold"
                      >
                        Instagram
                      </a>
                    )}
                    {profile.profile.facebook && (
                      <a
                        href={getSocialUrl('facebook', profile.profile.facebook) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 rounded-lg px-4 py-2 font-semibold"
                      >
                        Facebook
                      </a>
                    )}
                    {profile.profile.x_twitter && (
                      <a
                        href={getSocialUrl('x_twitter', profile.profile.x_twitter) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 rounded-lg px-4 py-2 font-semibold"
                      >
                        X (Twitter)
                      </a>
                    )}
                    {profile.profile.tiktok && (
                      <a
                        href={getSocialUrl('tiktok', profile.profile.tiktok) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-black hover:bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 font-semibold"
                      >
                        TikTok
                      </a>
                    )}
                    {profile.profile.snapchat && (
                      <a
                        href={getSocialUrl('snapchat', profile.profile.snapchat) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-500 text-black rounded-lg px-4 py-2 font-semibold"
                      >
                        Snapchat
                      </a>
                    )}
                    {profile.profile.youtube && (
                      <a
                        href={getSocialUrl('youtube', profile.profile.youtube) || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 rounded-lg px-4 py-2 font-semibold"
                      >
                        YouTube
                      </a>
                    )}
                  </div>
                </div>
              </>
            )}

            {/* No Profile Data */}
            {!profile.profile && (
              <div className="text-center py-8 text-gray-400">
                <p>This contestant hasn't set up their profile yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => router.push('/')}
            className="bg-gray-800 hover:bg-gray-700 rounded-lg px-6 py-3 font-semibold"
          >
            ← Back to RodeoAI
          </button>
        </div>
      </div>
    </div>
  );
}
