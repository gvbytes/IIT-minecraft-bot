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

## 💻 Running Locally

```bash
# Clone the repository
git clone https://github.com/gvbytes/IITK-minecraft-bot.git
cd IITK-minecraft-bot

# Install dependencies
pip install -r requirements.txt

# Create your settings file, then put your bot token in it
cp .env.example .env

# Run the bot
python main.py
```

Settings (in `.env` locally, or as environment variables on your host):
- `DISCORD_BOT_TOKEN` (required): your bot token from the Discord Developer Portal
- `MINECRAFT_SERVER_IP` (optional): shown by the `/ip` command
- `PORT` (optional, default `10000`): port for the keep-alive web server

`.env` is listed in `.gitignore`, so your token is never committed.
