#!/usr/bin/env python3
"""
Script to regenerate Google Calendar OAuth token.

This script will:
1. Delete the existing token file
2. Trigger a new OAuth flow
3. Save the new token

Run this if you're getting "invalid_scope" or token expiration errors.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.src.google_auth_provider import GoogleAuthProvider

def regenerate_token():
    """Regenerate the Google Calendar OAuth token."""
    token_file = project_root / "app" / "src" / "token.json"
    credentials_file = project_root / "app" / "creds" / "credentials.json"
    
    print("Regenerating Google Calendar OAuth token...")
    print(f"Token file: {token_file}")
    print(f"Credentials file: {credentials_file}")
    
    # Delete existing token if it exists
    if token_file.exists():
        print(f"\nDeleting existing token file: {token_file}")
        token_file.unlink()
        print("Token file deleted.")
    else:
        print("\nNo existing token file found.")
    
    # Check if credentials file exists
    if not credentials_file.exists():
        print(f"\nERROR: Credentials file not found: {credentials_file}")
        print("Please download your OAuth2 credentials from Google Cloud Console.")
        return False
    
    # Create auth provider and trigger OAuth flow
    try:
        print("\nStarting OAuth flow...")
        print("A browser window will open for you to authorize the application.")
        
        auth_provider = GoogleAuthProvider(
            scopes=["https://www.googleapis.com/auth/calendar"],
            credentials_file=str(credentials_file),
            token_file=str(token_file)
        )
        
        # This will trigger the OAuth flow
        credentials = auth_provider.get_credentials()
        
        print(f"\n✅ Token successfully generated and saved to: {token_file}")
        print("You can now use the calendar API.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during token generation: {e}")
        return False

if __name__ == "__main__":
    success = regenerate_token()
    sys.exit(0 if success else 1)

