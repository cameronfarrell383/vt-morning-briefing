"""
One-time OAuth2 flow to obtain a Gmail refresh token.

Reads GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET from .env,
opens a browser for login, and prints the refresh token.
"""

import sys
import os

# Allow running from the auth/ directory or the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n=== Save this refresh token to GOOGLE_REFRESH_TOKEN in .env ===")
    print(creds.refresh_token)
    print("===============================================================\n")


if __name__ == "__main__":
    main()
