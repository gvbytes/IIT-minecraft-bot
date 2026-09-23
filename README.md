# 🏰 IITK Minecraft Discord Bot & Community Architect

Master bot and automation engine for the **IIT Kanpur Minecraft Community & SMP Discord Server**.
**Made using Antigravity**

---

## ⚡ Features
- **Automatic Server Architect:** Deploys structured categories, text channels, slowmodes, and permissions.
- **Hostel / Hall Selector:** Interactive Discord dropdown menu for all 15 halls (`Hall 1` - `Hall 14`, `GH / Towers`).
- **Interactive Role Toggles:** Clickable buttons for Java/Bedrock editions, playstyles (Redstone/Builder), and event notifications.
- **Interactive Whitelist Applications:** Pinned modal button for student applications (IGN, Edition, Roll No., Hostel) with one-click **`[✅ Approve]`** / **`[❌ Reject]`** buttons for staff.
- **Anti-Grief Support Desk:** One-click private ticket launcher for CoreProtect rollbacks and server bug reporting.
- **Render Keep-Alive Web Server:** Built-in `aiohttp` web server listening on `$PORT` to support Render's Free Web Service tier.

---

## 🚀 Deploying on Render (Free Tier)

### Step 1: Create a New Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository: `https://github.com/gvbytes/IIT-minecraft-bot`.
4. Configure the settings:
   - **Name:** `iitk-minecraft-bot`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** `Free`

### Step 2: Set Environment Variables on Render
In the **Environment Variables** section, add:
- `DISCORD_BOT_TOKEN`: *Your bot token from the Discord Developer Portal*
- `MINECRAFT_SERVER_IP`: *(Optional)* Your campus LAN IP or Playit.gg tunnel address.
- `PORT`: `10000` *(Render sets this automatically)*

Click **Deploy Web Service**!

---

### 💡 How to Keep the Bot Awake 24/7 on Render Free Tier
Render free web services spin down after 15 minutes of inactivity. Because this bot includes a lightweight HTTP endpoint on `/`, you can keep it running 24/7 for free:
1. Copy your Render web service URL (e.g. `https://iitk-minecraft-bot.onrender.com`).
2. Go to a free monitoring service like [UptimeRobot](https://uptimerobot.com/) or [cron-job.org](https://cron-job.org/).
3. Add a monitor to send an HTTP GET request to `https://iitk-minecraft-bot.onrender.com/health` every **10 minutes**.
4. Your bot will remain online 24/7 without sleeping!

---

## 💻 Running Locally

```bash
# Clone the repository
git clone https://github.com/gvbytes/IIT-minecraft-bot.git
cd IIT-minecraft-bot

# Install dependencies
pip install -r requirements.txt

# Run the bot
export DISCORD_BOT_TOKEN="your_bot_token_here"
python main.py
```
