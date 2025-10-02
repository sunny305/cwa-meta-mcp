#!/usr/bin/env python3
"""
Simple token generator for Facebook Ads API.
This script exchanges a short-lived token from Graph API Explorer for a long-lived token.

NO REDIRECT URI NEEDED - This method doesn't require OAuth redirect configuration.
"""

import os
import sys
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

FB_APP_ID = os.getenv('FB_APP_ID')
FB_APP_SECRET = os.getenv('FB_APP_SECRET')
API_VERSION = 'v23.0'

def get_long_lived_token(short_token):
    """Exchange short-lived token for long-lived token (60 days)"""
    url = f'https://graph.facebook.com/{API_VERSION}/oauth/access_token'
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': FB_APP_ID,
        'client_secret': FB_APP_SECRET,
        'fb_exchange_token': short_token
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('access_token')
    except Exception as e:
        print(f"❌ Error getting long-lived token: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_token_info(access_token):
    """Get information about the access token"""
    url = f'https://graph.facebook.com/{API_VERSION}/debug_token'
    params = {
        'input_token': access_token,
        'access_token': f"{FB_APP_ID}|{FB_APP_SECRET}"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {})
    except Exception as e:
        print(f"⚠️  Warning: Could not get token info: {e}")
        return {}

def save_token_to_env(token):
    """Save the access token to .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        set_key(env_path, 'FB_ACCESS_TOKEN', token)
        return True
    except Exception as e:
        print(f"Error saving token to .env: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("🔑 Facebook Ads API Token Generator")
    print("="*80)

    # Validate configuration
    if not FB_APP_ID or not FB_APP_SECRET:
        print("\n❌ ERROR: Missing configuration")
        print("\nPlease add these to your .env file:")
        print("  FB_APP_ID=\"your_app_id\"")
        print("  FB_APP_SECRET=\"your_app_secret\"\n")
        return 1

    print("\n✓ Configuration loaded")
    print(f"  App ID: {FB_APP_ID}")

    print("\n" + "="*80)
    print("📝 Instructions:")
    print("="*80)
    print("\n1. Go to: https://developers.facebook.com/tools/explorer/")
    print("2. Select your app from the dropdown")
    print("3. Click 'Generate Access Token'")
    print("4. Select these permissions:")
    print("   - ads_read")
    print("   - ads_management")
    print("   - business_management")
    print("5. Copy the generated token")
    print("\n" + "="*80)

    # Get token from user
    print("\n📋 Paste your short-lived token below:")
    short_token = input("> ").strip()

    if not short_token:
        print("\n❌ No token provided. Exiting.")
        return 1

    print("\n⏳ Converting to long-lived token...")

    # Exchange for long-lived token
    long_token = get_long_lived_token(short_token)

    if not long_token:
        print("\n❌ Failed to generate long-lived token.")
        print("\nTroubleshooting:")
        print("1. Make sure your App ID and App Secret are correct")
        print("2. Ensure the token is from Graph API Explorer")
        print("3. Check that your app has Marketing API access")
        return 1

    # Get token info
    print("\n✓ Long-lived token generated!")
    token_info = get_token_info(long_token)

    # Save to .env
    saved = save_token_to_env(long_token)

    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print("="*80)

    if saved:
        print("\n✓ Token saved to .env file")
    else:
        print("\n⚠️  Could not save to .env automatically")

    print("\n📋 Your Long-Lived Access Token:")
    print("-" * 80)
    print(long_token)
    print("-" * 80)

    if token_info:
        print("\n📊 Token Details:")
        print(f"  User ID: {token_info.get('user_id', 'N/A')}")
        print(f"  App ID: {token_info.get('app_id', 'N/A')}")
        print(f"  Valid: {'Yes ✓' if token_info.get('is_valid') else 'No ✗'}")
        print(f"  Expires: {'~60 days' if token_info.get('data_access_expires_at') else 'Check Facebook'}")

        scopes = token_info.get('scopes', [])
        if scopes:
            print(f"\n  Permissions:")
            for scope in scopes:
                print(f"    • {scope}")

    if not saved:
        print("\n📝 Manual Setup:")
        print(f'Add this to your .env file:')
        print(f'FB_ACCESS_TOKEN="{long_token}"')

    print("\n" + "="*80)
    print("🚀 Next Steps:")
    print("="*80)
    print("\n1. Test the token:")
    print("   python server.py --fb-token YOUR_TOKEN")
    print("\n2. Or use with MCP clients (Claude Desktop, Cursor, etc.)")
    print("\n" + "="*80 + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
