# Contestant Social Profiles Feature

## Overview

The Contestant Social Profiles feature allows rodeo contestants to create a comprehensive "digital rodeo card" that showcases their social media presence, rodeo achievements, and personal information. This creates a centralized hub for fans, rodeo organizers, and sponsors to connect with contestants.

## Features

### For Contestants

1. **Profile Management**
   - Create and update social media links (Instagram, Facebook, X/Twitter, TikTok, Snapchat, YouTube)
   - Add hometown and rodeo events information
   - Write a personal bio
   - All profiles are shareable via unique URLs

2. **Social Media Integration**
   - Direct links to all social platforms
   - Clean, professional presentation
   - Easy sharing with fans and sponsors

3. **Verified Status** (Pro tier)
   - Blue verification badge for authenticated contestants
   - Increased credibility and visibility

### For Fans & Organizers

1. **Public Profile View**
   - Beautiful, mobile-friendly profile pages
   - Direct follow buttons for all social platforms
   - View contestant's rodeo information and bio
   - Shareable URLs: `rodeoai.com/profile/{username}`

## API Endpoints

### Authentication

```
POST /api/auth/register
POST /api/auth/token
GET  /api/auth/me
```

### Contestant Profiles

```
POST   /api/contestants/me          # Create profile
PATCH  /api/contestants/me          # Update profile
GET    /api/contestants/me          # Get own profile
GET    /api/contestants/{username}  # Get public profile
```

## Database Schema

### User Table
- id (Primary Key)
- email (Unique)
- username (Unique)
- hashed_password
- full_name
- is_active
- is_pro (for Pro tier features)
- created_at
- updated_at

### ContestantProfile Table
- id (Primary Key)
- user_id (Foreign Key to User, Unique)
- instagram
- facebook
- snapchat
- tiktok
- x_twitter
- youtube
- hometown
- events
- bio
- is_verified
- created_at
- updated_at

## Usage

### Creating a Profile

1. User registers/logs in through the web interface
2. Clicks on their username in the top-right corner
3. Selects "Profile Settings"
4. Fills out social media handles and rodeo information
5. Clicks "Create Profile" or "Update Profile"

### Viewing Public Profiles

Navigate to: `/profile/{username}`

Example: `/profile/trevor-brazile`

## Frontend Components

- `AuthModal.tsx` - Login/Registration modal
- `ProfileSettingsModal.tsx` - Profile editing interface
- `app/profile/[username]/page.tsx` - Public profile view page
- `lib/AuthContext.tsx` - Authentication state management
- `lib/api.ts` - API client functions

## Future Enhancements

### Planned Features

1. **Link-in-Bio Feature**
   - Custom short URLs (e.g., `rodeoai.me/jbmauney`)
   - Stats dashboard showing profile views
   - Replace generic Linktree services

2. **Social Media Verification**
   - Manual verification process for Pro users
   - "Verified Athlete" badge

3. **Automated Result Sharing**
   - One-click social media posts after rodeos
   - Auto-generated graphics with scores and RodeoAI branding
   - Instagram Stories integration

4. **Analytics**
   - Profile view counts
   - Social link click tracking
   - Engagement metrics

5. **QR Code Generation**
   - Printable QR codes for autograph cards
   - Easy profile sharing at events

## Setup Instructions

### Backend

1. Install dependencies:
   ```bash
   cd Desktop/rodeoai-backend
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY and OPENAI_API_KEY
   ```

3. Run the server:
   ```bash
   python main.py
   ```

The database will be automatically created on first run.

### Frontend

The frontend is integrated into the main Next.js application. The AuthProvider wraps the entire app in `layout.tsx`, providing authentication context to all components.

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Token expiration: 30 minutes
- CORS configured for frontend access
- Input validation on all endpoints

## API Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contestant@example.com",
    "username": "rodeochamp",
    "password": "secure_password",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -d "username=rodeochamp&password=secure_password"
```

### Create/Update Profile

```bash
curl -X PATCH http://localhost:8000/api/contestants/me \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram": "rodeochamp",
    "hometown": "Houston, TX",
    "events": "Team Roping (Header)",
    "bio": "2x NFR qualifier. Living the dream."
  }'
```

### Get Public Profile

```bash
curl http://localhost:8000/api/contestants/rodeochamp
```

## Notes

- This is the foundation for the "Digital Rodeo Card" concept
- All features align with RodeoAI's custom branding and DataSpur identity
- Built for scalability and future enhancements
- Mobile-first design for contestant and fan experience
