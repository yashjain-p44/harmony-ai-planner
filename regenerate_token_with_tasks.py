#!/usr/bin/env python3
"""
Regenerate Google OAuth token with both Calendar and Tasks scopes.

This script will delete the existing token and prompt for re-authentication
with the required scopes for both Calendar and Tasks APIs.

Usage:
    python regenerate_token_with_tasks.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add src to path
src_path = project_root / "app" / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from google_auth_provider import GoogleAuthProvider

def main():
    """Regenerate token with both calendar and tasks scopes."""
    token_file = src_path / "token.json"
    credentials_file = project_root / "app" / "creds" / "credentials.json"
    
    print("=" * 60)
    print("Regenerate Google OAuth Token with Calendar and Tasks Scopes")
    print("=" * 60)
    print(f"\nToken file: {token_file}")
    print(f"Credentials file: {credentials_file}")
    
    # Check if credentials file exists
    if not credentials_file.exists():
        print(f"\n❌ ERROR: Credentials file not found: {credentials_file}")
        print("Please download your OAuth2 credentials from Google Cloud Console.")
        return False
    
    # Delete existing token if it exists
    if token_file.exists():
        print(f"\n⚠️  Found existing token at: {token_file}")
        print("The existing token only has calendar scope.")
        print("We need to regenerate it with both calendar and tasks scopes.")
        response = input("\nDelete existing token and re-authenticate? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False
        
        print(f"\nDeleting existing token...")
        os.remove(token_file)
        print("✓ Token deleted.")
    
    # Create auth provider with both scopes
    print("\n" + "=" * 60)
    print("Initializing auth provider with Calendar and Tasks scopes...")
    print("=" * 60)
    
    try:
        auth_provider = GoogleAuthProvider(
            scopes=[
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/tasks"
            ],
            credentials_file=str(credentials_file),
            token_file=str(token_file)
        )
        
        print("\n🔐 Starting OAuth flow...")
        print("A browser window will open for you to authorize the application.")
        print("Please grant permissions for both Calendar and Tasks.")
        
        # This will trigger the OAuth flow
        credentials = auth_provider.get_credentials()
        
        print("\n" + "=" * 60)
        print("✅ Successfully authenticated!")
        print("=" * 60)
        print(f"\nToken saved to: {token_file}")
        print("Scopes granted:", credentials.scopes)
        print("\nYou can now use both Calendar and Tasks APIs.")
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
