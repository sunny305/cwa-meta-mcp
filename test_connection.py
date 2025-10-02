#!/usr/bin/env python3
"""
Quick test script to verify Facebook Ads API connection
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
API_VERSION = 'v23.0'

def test_connection():
    print("\n" + "="*80)
    print("🧪 Testing Facebook Ads API Connection")
    print("="*80)

    if not FB_ACCESS_TOKEN:
        print("\n❌ No access token found in .env file")
        return False

    print(f"\n✓ Token found (length: {len(FB_ACCESS_TOKEN)} chars)")

    # Test 1: Get user info
    print("\n📱 Test 1: Getting user info...")
    url = f'https://graph.facebook.com/{API_VERSION}/me'
    params = {'access_token': FB_ACCESS_TOKEN}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        user_data = response.json()
        print(f"✅ Success! User: {user_data.get('name', 'N/A')} (ID: {user_data.get('id', 'N/A')})")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 2: Get ad accounts
    print("\n💼 Test 2: Getting ad accounts...")
    url = f'https://graph.facebook.com/{API_VERSION}/me/adaccounts'
    params = {
        'access_token': FB_ACCESS_TOKEN,
        'fields': 'id,name,account_status'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        accounts_data = response.json()
        accounts = accounts_data.get('data', [])

        if accounts:
            print(f"✅ Success! Found {len(accounts)} ad account(s):")
            for i, acc in enumerate(accounts, 1):
                print(f"   {i}. {acc.get('name', 'N/A')} (ID: {acc.get('id', 'N/A')}) - Status: {acc.get('account_status', 'N/A')}")
        else:
            print("⚠️  No ad accounts found. You may need to:")
            print("   - Link an ad account in Business Manager")
            print("   - Grant app access to ad accounts")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 3: Check token permissions
    print("\n🔑 Test 3: Checking token permissions...")
    url = f'https://graph.facebook.com/{API_VERSION}/debug_token'
    app_id = os.getenv('FB_APP_ID')
    app_secret = os.getenv('FB_APP_SECRET')

    if app_id and app_secret:
        params = {
            'input_token': FB_ACCESS_TOKEN,
            'access_token': f"{app_id}|{app_secret}"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            debug_data = response.json().get('data', {})

            scopes = debug_data.get('scopes', [])
            is_valid = debug_data.get('is_valid', False)

            print(f"✅ Token Status: {'Valid' if is_valid else 'Invalid'}")
            print(f"   Permissions: {', '.join(scopes) if scopes else 'None'}")

            # Check for required permissions
            required = ['ads_read', 'ads_management', 'business_management']
            missing = [p for p in required if p not in scopes]

            if missing:
                print(f"\n⚠️  Missing permissions: {', '.join(missing)}")
            else:
                print(f"\n✅ All required permissions present!")

        except Exception as e:
            print(f"⚠️  Could not verify permissions: {e}")

    print("\n" + "="*80)
    print("✅ Connection Test Complete!")
    print("="*80)
    print("\n🚀 Your MCP server is ready to use!")
    print("   Add it to Claude Desktop or Cursor to start managing ads.\n")

    return True

if __name__ == '__main__':
    test_connection()
