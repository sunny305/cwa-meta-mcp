#!/usr/bin/env python3
"""
Self-hosted OAuth server to generate Meta/Facebook access tokens.
Run this server, visit http://localhost:8000, and authorize to get a long-lived token.
Follows Meta's official OAuth flow: https://developers.facebook.com/docs/facebook-login/guides/advanced/manual-flow/

This replaces the need for third-party OAuth services - everything runs locally on your machine.
"""

import os
import sys
import secrets
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv, set_key

load_dotenv()

FB_APP_ID = os.getenv('FB_APP_ID')
FB_APP_SECRET = os.getenv('FB_APP_SECRET')
REDIRECT_URI = 'http://localhost:8000/callback'
API_VERSION = 'v23.0'  # Latest stable version

# Permissions needed for Meta Ads API
# Note: These require App Review for production, but work in Development Mode
# if you're added as an Admin/Developer/Tester in the app
PERMISSIONS = [
    'ads_read',
    'ads_management',
    'business_management',
    'read_insights'
]

# For testing without app review, you can temporarily use basic permissions:
# PERMISSIONS = ['public_profile', 'email']
# Then manually generate a token via Graph API Explorer with ads permissions

# CSRF protection: Store state token
STATE_TOKEN = None

def save_token_to_env(token):
    """Save the access token to .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        set_key(env_path, 'FB_ACCESS_TOKEN', token)
        return True
    except Exception as e:
        print(f"Error saving token to .env: {e}")
        return False

class OAuthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        global STATE_TOKEN
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # Step 1: Generate CSRF token and redirect to Facebook OAuth
            STATE_TOKEN = secrets.token_urlsafe(32)

            params = {
                'client_id': FB_APP_ID,
                'redirect_uri': REDIRECT_URI,
                'state': STATE_TOKEN,
                'scope': ','.join(PERMISSIONS),
                'response_type': 'code'
            }

            auth_url = f"https://www.facebook.com/{API_VERSION}/dialog/oauth?{urlencode(params)}"

            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif parsed_path.path == '/callback':
            # Step 2: Handle OAuth callback
            query_params = parse_qs(parsed_path.query)

            # Validate state token (CSRF protection)
            if 'state' in query_params:
                received_state = query_params['state'][0]
                if received_state != STATE_TOKEN:
                    self.send_error(403, "Invalid state parameter. Possible CSRF attack.")
                    return
            else:
                self.send_error(400, "Missing state parameter")
                return

            if 'code' in query_params:
                code = query_params['code'][0]

                # Exchange code for access token
                token_url = f'https://graph.facebook.com/{API_VERSION}/oauth/access_token'
                params = {
                    'client_id': FB_APP_ID,
                    'client_secret': FB_APP_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                }

                try:
                    response = requests.get(token_url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    short_token = data.get('access_token')

                    # Exchange for long-lived token (60 days)
                    long_token = self.get_long_lived_token(short_token)

                    if long_token:
                        # Get token info
                        token_info = self.get_token_info(long_token)

                        # Auto-save token to .env
                        saved = save_token_to_env(long_token)

                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()

                        save_status = "✓ Token saved to .env file" if saved else "⚠ Could not save to .env file automatically"
                        save_color = "#28a745" if saved else "#ffc107"

                        html = f"""
                        <html>
                        <head><title>Meta Ads OAuth Success</title></head>
                        <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
                            <h1 style="color: #1877f2;">✓ Authorization Successful!</h1>
                            <p>Your long-lived access token has been generated and is ready to use.</p>

                            <div style="background: {save_color}; color: white; padding: 10px; border-radius: 5px; margin: 20px 0;">
                                {save_status}
                            </div>

                            <h2>Access Token:</h2>
                            <textarea id="tokenArea" readonly style="width: 100%; height: 100px; padding: 10px; font-family: monospace; font-size: 12px;">{long_token}</textarea>

                            <div style="margin: 15px 0;">
                                <button onclick="copyToken()" id="copyBtn"
                                        style="background: #1877f2; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; margin-right: 10px;">
                                    📋 Copy Token to Clipboard
                                </button>
                            </div>

                            <h2>Token Details:</h2>
                            <ul>
                                <li><strong>Type:</strong> {token_info.get('type', 'N/A')}</li>
                                <li><strong>App ID:</strong> {token_info.get('app_id', 'N/A')}</li>
                                <li><strong>User ID:</strong> {token_info.get('user_id', 'N/A')}</li>
                                <li><strong>Expires:</strong> {token_info.get('expires_at', 'Never') if token_info.get('expires_at') != 0 else 'Never'}</li>
                                <li><strong>Valid:</strong> {"Yes ✓" if token_info.get('is_valid') else "No ✗"}</li>
                            </ul>

                            <h3>Granted Permissions:</h3>
                            <ul>
                                {"".join([f"<li>{scope}</li>" for scope in token_info.get('scopes', [])])}
                            </ul>

                            <h2>Next Steps:</h2>
                            <ol>
                                {'<li style="text-decoration: line-through;">Token already saved to .env file ✓</li>' if saved else '<li>Manually add token to .env file: <code>FB_ACCESS_TOKEN="YOUR_TOKEN"</code></li>'}
                                <li>Start the MCP server: <code>python server.py --fb-token YOUR_TOKEN</code></li>
                                <li>Or configure your MCP client (Claude Desktop, Cursor, etc.)</li>
                            </ol>

                            <p style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                                <strong>⏰ Token Expiration:</strong> This token is valid for ~60 days. Run this OAuth flow again when it expires.
                            </p>

                            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                                🎉 You're all set! This window will close automatically in a few seconds.
                            </p>

                            <script>
                                function copyToken() {{
                                    const tokenArea = document.getElementById('tokenArea');
                                    tokenArea.select();
                                    document.execCommand('copy');
                                    const btn = document.getElementById('copyBtn');
                                    btn.textContent = '✓ Copied!';
                                    btn.style.background = '#28a745';
                                    setTimeout(() => {{
                                        btn.textContent = '📋 Copy Token to Clipboard';
                                        btn.style.background = '#1877f2';
                                    }}, 2000);
                                }}
                            </script>
                        </body>
                        </html>
                        """

                        self.wfile.write(html.encode())

                        # Print to console as well
                        print("\n" + "="*80)
                        print("SUCCESS! Your Meta Ads Access Token:")
                        print("="*80)
                        print(f"\n{long_token}\n")
                        print("="*80)
                        print(f"Token Type: {token_info.get('type', 'N/A')}")
                        print(f"User ID: {token_info.get('user_id', 'N/A')}")
                        print(f"Valid: {'Yes' if token_info.get('is_valid') else 'No'}")
                        print(f"Scopes: {', '.join(token_info.get('scopes', []))}")
                        print("="*80)
                        print("\nUpdate your .env file with:")
                        print(f'FB_ACCESS_TOKEN="{long_token}"')
                        print("="*80 + "\n")

                        # Shutdown server after successful auth
                        import threading
                        threading.Timer(2.0, lambda: os._exit(0)).start()

                    else:
                        self.send_error(500, "Failed to get long-lived token")

                except Exception as e:
                    self.send_error(500, f"Error: {str(e)}")

            elif 'error' in query_params:
                error = query_params['error'][0]
                error_desc = query_params.get('error_description', ['Unknown error'])[0]

                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                html = f"""
                <html>
                <body style="font-family: Arial; padding: 40px;">
                    <h1 style="color: red;">Authorization Failed</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_desc}</p>
                    <p><a href="/">Try again</a></p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())

        else:
            self.send_error(404, "Not Found")

    def get_long_lived_token(self, short_token):
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
            print(f"Error getting long-lived token: {e}")
            return None

    def get_token_info(self, access_token):
        """Get information about the access token (for validation)"""
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
            print(f"Error getting token info: {e}")
            return {}

def main():
    # Validate configuration
    if not FB_APP_ID or not FB_APP_SECRET:
        print("\n" + "="*80)
        print("❌ ERROR: Missing Facebook App Configuration")
        print("="*80)
        print("\nYou need to set up your Facebook App credentials first:\n")
        print("1. Go to https://developers.facebook.com/apps")
        print("2. Create a new app or use an existing one")
        print("3. Copy your App ID and App Secret")
        print("4. Add them to your .env file:\n")
        print("   FB_APP_ID=\"your_app_id\"")
        print("   FB_APP_SECRET=\"your_app_secret\"\n")
        print("5. Make sure to add this redirect URI in your Facebook App settings:")
        print("   http://localhost:8000/callback\n")
        print("="*80 + "\n")
        return 1

    PORT = 8000
    server = HTTPServer(('localhost', PORT), OAuthHandler)

    print("\n" + "="*80)
    print("🚀 Self-Hosted Meta Ads OAuth Server")
    print("="*80)
    print("\n✓ Configuration validated")
    print(f"✓ App ID: {FB_APP_ID}")
    print(f"✓ Redirect URI: http://localhost:{PORT}/callback")
    print(f"\n📱 Required Permissions: {', '.join(PERMISSIONS)}")
    print("\n" + "="*80)
    print("\n🔗 Open this URL in your browser to authenticate:\n")
    print(f"   👉 http://localhost:{PORT}\n")
    print("="*80)
    print("\n⏳ Waiting for authorization...")
    print("(The server will automatically shutdown after successful authorization)\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user.")
        server.shutdown()
    except Exception as e:
        print(f"\n\n❌ Server error: {e}")
        server.shutdown()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
