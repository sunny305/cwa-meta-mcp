# Facebook/Meta Ads MCP Server

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/gomarble-ai/facebook-ads-mcp-server)](https://archestra.ai/mcp-catalog/gomarble-ai__facebook-ads-mcp-server)
[![smithery badge](https://smithery.ai/badge/@gomarble-ai/facebook-ads-mcp-server)](https://smithery.ai/server/@gomarble-ai/facebook-ads-mcp-server)

This project provides an MCP server acting as an interface to the Meta Ads, enabling programmatic access to Meta Ads data and management features.

## 🚀 Quick Start (3 Steps!)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env (add your Facebook App ID and Secret)
cp .env.example .env
# Edit .env with your credentials

# 3. Generate token (no redirect URI needed!)
python generate_token.py
# Follow the prompts to get your token from Graph API Explorer

# Done! Start the server
python server.py
```

<video controls width="1920" height="512" src="https://github.com/user-attachments/assets/c4a76dcf-cf5d-4a1d-b976-08165e880fe4">Your browser does not support the video tag.</video>

## Easy Token Setup (No Redirect URI Needed!)

This server includes a **simple token generator** - no OAuth redirect configuration required!

### Method 1: Graph API Explorer (Recommended - Easiest!)

**No redirect URI needed! Works immediately!**

1. Configure your `.env` file with App ID and Secret
2. Get a token from [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
3. Run: `python generate_token.py`
4. Paste your token when prompted
5. Token is automatically converted to long-lived (60 days) and saved!

**This is the easiest method and doesn't require any Facebook App configuration beyond creating the app.**

### Method 2: OAuth Server (Advanced - Requires Redirect URI Setup)

If you want to set up full OAuth flow (requires configuring redirect URI in Facebook App):

1. Add `http://localhost:8000/callback` to your Facebook App's redirect URIs
2. Run: `python oauth_server.py`
3. Open `http://localhost:8000` in your browser
4. Authenticate with Facebook

**Note:** OAuth method currently only works with basic permissions due to Facebook's App Review requirements for Ads API permissions.

---

## Setup

### Prerequisites

*   Python 3.10+
*   A Facebook/Meta Developer Account
*   A Facebook App (create one at https://developers.facebook.com/apps)
*   Dependencies listed in `requirements.txt`

### Installation Steps

1.  **(Optional but Recommended) Create and Activate a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

    Using a virtual environment helps manage project dependencies cleanly[[Source]](https://docs.python.org/3/tutorial/venv.html).

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Facebook App:**
    - Go to [Facebook Developers](https://developers.facebook.com/apps)
    - Create a new app or use an existing one (choose **"Business"** type if creating new)
    - **IMPORTANT:** Add **"Marketing API"** product to your app:
      - Click "Add Product" in left sidebar
      - Find "Marketing API" and click "Set Up"
    - Copy your App ID and App Secret
    - Create a `.env` file (see `.env.example`):
    ```bash
    FB_APP_ID="your_app_id_here"
    FB_APP_SECRET="your_app_secret_here"
    ```

    **Trouble seeing ads permissions?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions on enabling Marketing API.

4.  **Generate Access Token (Recommended Method - No Redirect URI Needed):**

    **Using Token Generator Script:**
    ```bash
    python generate_token.py
    ```

    This will guide you through:
    1. Opening Graph API Explorer
    2. Selecting permissions: `ads_read`, `ads_management`, `business_management`
    3. Converting short-lived token to long-lived (60 days)
    4. Auto-saving to `.env` file

    **✓ No redirect URI configuration needed!**
    **✓ Works with Ads API permissions immediately!**

    **Alternative (Advanced):** Use `oauth_server.py` for full OAuth flow (requires redirect URI setup and currently limited to basic permissions without App Review).

### Usage with MCP Clients (e.g., Cursor, Claude Desktop)

To integrate this server with an MCP-compatible client, add a configuration([Claude](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server)) similar to the following. Replace `YOUR_META_ACCESS_TOKEN` with your actual token and adjust the path to `server.py` if necessary.

```json
{
  "mcpServers": {
    "fb-ads-mcp-server": {
      "command": "python",
      "args": [
        "/path/to/your/fb-ads-mcp-server/server.py",
        "--fb-token",
        "YOUR_META_ACCESS_TOKEN"
      ]
      // If using a virtual environment, you might need to specify the python executable within the venv:
      // "command": "/path/to/your/fb-ads-mcp-server/venv/bin/python",
      // "args": [
      //   "/path/to/your/fb-ads-mcp-server/server.py",
      //   "--fb-token",
      //   "YOUR_META_ACCESS_TOKEN"
      // ]
    }
  }
}
```
Restart the MCP Client app after making the update in the configuration.

*(Note: On Windows, you might need to adjust the command structure or use `cmd /k` depending on your setup.)*

### Debugging the Server

Execute `server.py`, providing the access token via the `--fb-token` argument.

```bash
python server.py --fb-token YOUR_META_ACCESS_TOKEN
```

Or use the token from `.env` file:

```bash
export FB_ACCESS_TOKEN="your_token_here"  # Linux/Mac
python server.py
```

### Token Generator (Recommended)

The included `generate_token.py` provides the easiest way to get a long-lived token:

```bash
python generate_token.py
```

This will:
1. Prompt you to get a token from Graph API Explorer
2. Exchange it for a long-lived token (60 days)
3. Validate the token and show permissions
4. Automatically save it to your `.env` file

**No redirect URI setup needed!** - Works immediately with Ads API permissions.

### OAuth Server (Advanced)

For those who want full OAuth flow, `oauth_server.py` is available:

```bash
python oauth_server.py
```

**Note:** Requires redirect URI setup in Facebook App and currently limited to basic permissions without Facebook App Review approval for Ads API access.

### Available MCP Tools

This MCP server provides tools for interacting with META Ads objects and data:

| Tool Name                       | Description                                              |
| ------------------------------- | -------------------------------------------------------- |
| **Account & Object Read**       |                                                          |
| `list_ad_accounts`              | Lists ad accounts linked to the token.                   |
| `get_details_of_ad_account`     | Retrieves details for a specific ad account.             |
| `get_campaign_by_id`            | Retrieves details for a specific campaign.               |
| `get_adset_by_id`               | Retrieves details for a specific ad set.                 |
| `get_ad_by_id`                  | Retrieves details for a specific ad.                     |
| `get_ad_creative_by_id`         | Retrieves details for a specific ad creative.            |
| `get_adsets_by_ids`             | Retrieves details for multiple ad sets by their IDs.     |
| **Fetching Collections**        |                                                          |
| `get_campaigns_by_adaccount`    | Retrieves campaigns within an ad account.                |
| `get_adsets_by_adaccount`       | Retrieves ad sets within an ad account.                  |
| `get_ads_by_adaccount`          | Retrieves ads within an ad account.                      |
| `get_adsets_by_campaign`        | Retrieves ad sets within a campaign.                     |
| `get_ads_by_campaign`           | Retrieves ads within a campaign.                         |
| `get_ads_by_adset`              | Retrieves ads within an ad set.                          |
| `get_ad_creatives_by_ad_id`     | Retrieves creatives associated with an ad.               |
| **Insights & Performance Data** |                                                          |
| `get_adaccount_insights`        | Retrieves performance insights for an ad account.        |
| `get_campaign_insights`         | Retrieves performance insights for a campaign.           |
| `get_adset_insights`            | Retrieves performance insights for an ad set.            |
| `get_ad_insights`               | Retrieves performance insights for an ad.                |
| `fetch_pagination_url`          | Fetches data from a pagination URL (e.g., from insights).|
| **Activity/Change History**     |                                                          |
| `get_activities_by_adaccount`   | Retrieves change history for an ad account.              |
| `get_activities_by_adset`       | Retrieves change history for an ad set.                  |

*(Note: Most tools support additional parameters like `fields`, `filtering`, `limit`, pagination, date ranges, etc. Refer to the detailed docstrings within `server.py` for the full list and description of arguments for each tool.)*

*(Note: If your Meta access token expires, you'll need to generate a new one and update the configuration file of the MCP Client with new token to continue using the tools.)*

### Dependencies

*   [mcp](https://pypi.org/project/mcp/) (>=1.6.0)
*   [requests](https://pypi.org/project/requests/) (>=2.32.3)

### License
This project is licensed under the MIT License.

---

## Installing via Smithery

To install Facebook Ads Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@gomarble-ai/facebook-ads-mcp-server):

```bash
npx -y @smithery/cli install @gomarble-ai/facebook-ads-mcp-server --client claude
```
# cwa-meta-mcp
