
# OAuth Setup Instructions for Neuronas

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API
4. Create OAuth 2.0 Client ID credentials
5. Add these authorized redirect URIs:
   - `https://YOUR_REPL_DOMAIN/auth/google/callback`
   - `http://localhost:5000/auth/google/callback` (for development)

6. Set environment variables in Replit Secrets:
   - `GOOGLE_OAUTH_CLIENT_ID`: Your client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET`: Your client secret
   - `REPLIT_DEV_DOMAIN`: Your repl domain (automatically set)

## Replit OAuth Setup

Replit OAuth is automatically configured when running on Replit platform. The `REPL_ID` environment variable is automatically set.

## Environment Variables Required

```bash
# Google OAuth (set in Replit Secrets)
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret

# Replit OAuth (automatically set)
REPL_ID=your_repl_id

# Session secret (set in Replit Secrets)
SESSION_SECRET=your_random_secret_key
```

## Testing OAuth

1. Start your application
2. Navigate to `/auth/google/login` for Google OAuth
3. Navigate to `/auth/replit/login` for Replit OAuth
4. Both should redirect properly and create user accounts

## Callback URLs

- Google: `https://YOUR_DOMAIN/auth/google/callback`
- Replit: `https://YOUR_DOMAIN/auth/replit_auth/callback`

## Security Notes

- All OAuth flows include state validation
- Email verification is required for Google OAuth
- Sessions are properly managed and cleared on logout
- Safe URL validation prevents open redirects
