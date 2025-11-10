const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_pro: boolean;
  created_at: string;
}

export interface ContestantProfile {
  id: number;
  user_id: number;
  instagram?: string;
  facebook?: string;
  snapchat?: string;
  tiktok?: string;
  x_twitter?: string;
  youtube?: string;
  hometown?: string;
  events?: string;
  bio?: string;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PublicProfile {
  username: string;
  full_name?: string;
  profile?: ContestantProfile;
}

// Auth API
export async function register(email: string, username: string, password: string, full_name?: string) {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password, full_name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

export async function login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/api/auth/token`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get user info');
  }

  return response.json();
}

// Profile API
export async function getMyProfile(token: string): Promise<ContestantProfile> {
  const response = await fetch(`${API_BASE}/api/contestants/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get profile');
  }

  return response.json();
}

export async function createProfile(token: string, profile: Partial<ContestantProfile>): Promise<ContestantProfile> {
  const response = await fetch(`${API_BASE}/api/contestants/me`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create profile');
  }

  return response.json();
}

export async function updateProfile(token: string, profile: Partial<ContestantProfile>): Promise<ContestantProfile> {
  const response = await fetch(`${API_BASE}/api/contestants/me`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update profile');
  }

  return response.json();
}

export async function getPublicProfile(username: string): Promise<PublicProfile> {
  const response = await fetch(`${API_BASE}/api/contestants/${username}`);

  if (!response.ok) {
    throw new Error('Profile not found');
  }

  return response.json();
}
