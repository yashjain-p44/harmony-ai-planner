"""
Google Authentication Provider

This module provides a centralized authentication provider for Google APIs.
It handles OAuth2 flow, credential management, and token refresh, allowing
multiple Google service repositories to share the same authentication.
"""

import os
from typing import List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAuthProvider:
    """
    Centralized authentication provider for Google APIs.
    
    Handles OAuth2 authentication flow, credential loading/saving,
    and token refresh. Can be shared across multiple Google service
    repositories (Calendar, Tasks, etc.).
    """
    
    def __init__(
        self,
        scopes: List[str],
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """
        Initialize the Google Authentication Provider.
        
        Args:
            scopes: List of OAuth2 scopes required for the services.
                   Example: ["https://www.googleapis.com/auth/calendar",
                            "https://www.googleapis.com/auth/tasks"]
            credentials_file: Path to the OAuth2 credentials JSON file.
                            If None, uses default path: app/creds/credentials.json
            token_file: Path to store/load the token JSON file.
                       If None, uses default path: app/src/token.json
        """
        self.scopes = scopes
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths if not provided
        if credentials_file is None:
            credentials_file = os.path.join(script_dir, "..", "creds", "credentials.json")
        if token_file is None:
            token_file = os.path.join(script_dir, "token.json")
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self._credentials: Optional[Credentials] = None
    
    def get_credentials(self) -> Credentials:
        """
        Get authenticated credentials. If not authenticated or expired,
        will trigger authentication flow or refresh token.
        
        Returns:
            Authenticated Credentials object.
        
        Raises:
            FileNotFoundError: If credentials file is not found.
        """
        # Return cached credentials if valid
        if self._credentials and self._credentials.valid:
            return self._credentials
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            self._credentials = Credentials.from_authorized_user_file(
                self.token_file, self.scopes
            )
        
        # If there are no (valid) credentials available, authenticate
        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                # Refresh expired token
                self._credentials.refresh(Request())
            else:
                # Run OAuth flow
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download your OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                self._credentials = flow.run_local_server(port=0)
            
            # Save credentials for next run
            self._save_credentials()
        
        return self._credentials
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self._credentials:
            with open(self.token_file, "w") as token:
                token.write(self._credentials.to_json())
    
    def refresh_credentials(self) -> Credentials:
        """
        Force refresh of credentials.
        
        Returns:
            Refreshed Credentials object.
        """
        if self._credentials and self._credentials.refresh_token:
            self._credentials.refresh(Request())
            self._save_credentials()
        else:
            # If no refresh token, need to re-authenticate
            self._credentials = None
            return self.get_credentials()
        
        return self._credentials
    
    def clear_credentials(self) -> None:
        """Clear cached credentials (useful for testing or re-authentication)."""
        self._credentials = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

