#!/usr/bin/env python3
"""
IITK Minecraft Community & SMP Master Bot
Designed for 24/7 deployment on Render (includes aiohttp health check server).
"""

import sys
import os
import ssl
import certifi
import asyncio
from typing import Optional
from aiohttp import web

# Fix macOS SSL Certificates
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!iitk", intents=intents)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip() or (sys.argv[1].strip() if len(sys.argv) > 1 else "")
SERVER_IP = os.environ.get("MINECRAFT_SERVER_IP", "").strip() or (sys.argv[2].strip() if len(sys.argv) > 2 else "")
PORT = int(os.environ.get("PORT", 10000))

# --- Role Hierarchy Specification ---
ROLES_SPEC = [
    {"name": "👑 Server Admin / OP", "color": discord.Color.from_rgb(231, 76, 60), "hoist": True, "mentionable": True},
    {"name": "⚙️ SysAdmin / Host", "color": discord.Color.from_rgb(155, 89, 182), "hoist": True, "mentionable": True},
    {"name": "🛡️ Moderator", "color": discord.Color.from_rgb(46, 204, 113), "hoist": True, "mentionable": True},
    {"name": "🎓 Verified IITKian", "color": discord.Color.from_rgb(33, 150, 243), "hoist": True, "mentionable": False},
    {"name": "⛏️ SMP Whitelisted", "color": discord.Color.from_rgb(26, 188, 156), "hoist": True, "mentionable": True},
    {"name": "⚡ Redstone Engineer", "color": discord.Color.from_rgb(230, 126, 34), "hoist": False, "mentionable": False},
    {"name": "🎨 Master Builder", "color": discord.Color.from_rgb(241, 196, 15), "hoist": False, "mentionable": False},
    {"name": "⚔️ PvP / Tourneys", "color": discord.Color.from_rgb(233, 30, 99), "hoist": False, "mentionable": False},
    {"name": "📢 Event Pings", "color": discord.Color.from_rgb(255, 171, 0), "hoist": False, "mentionable": True},
    {"name": "⚠️ Server Restarts", "color": discord.Color.from_rgb(255, 87, 34), "hoist": False, "mentionable": True},
    {"name": "💻 Java Edition", "color": discord.Color.from_rgb(52, 152, 219), "hoist": False, "mentionable": False},
    {"name": "📱 Bedrock / PE", "color": discord.Color.from_rgb(0, 184, 217), "hoist": False, "mentionable": False},
    {"name": "🌐 Guest / Visitor", "color": discord.Color.from_rgb(149, 165, 166), "hoist": False, "mentionable": False},
]

HALL_ROLES = [
    "🏰 Hall 1", "🏰 Hall 2", "🏰 Hall 3", "🏰 Hall 4", "🏰 Hall 5",
    "🏰 Hall 6", "🏰 Hall 7", "🏰 Hall 8", "🏰 Hall 9", "🏰 Hall 10",
    "🏰 Hall 11", "🏰 Hall 12", "🏰 Hall 13", "🏰 Hall 14", "🏰 GH / Towers"
]

# --- Complete Master Channel Structure ---
STRUCTURE = {
    "📌 ── WELCOME & INFO ──": {
        "text": [
            ("📜・rules-and-conduct", "Official server rules, griefing policy, and IITK honor code.", True, 0),
            ("🌐・server-ip-and-guide", "Connection address, Java/Bedrock ports, campus LAN info, and Dynmap.", True, 0),
            ("🎭・pick-your-roles", "Self-assign your Hall, Edition, Playstyle, and Notification pings.", True, 0),
            ("📢・announcements", "Server restarts, season resets, updates, and maintenance alerts.", True, 0),
            ("📋・whitelist-requests", "Apply for whitelist access using the interactive button below.", False, 10),
            ("👋・welcome-lobby", "Say hello to new campus crafters joining the server!", False, 3),
        ],
        "voice": []
    },
    "⛏️ ── IITK MINECRAFT SMP ──": {
        "text": [
            ("💬・in-game-chat", "Synced live with Minecraft in-game chat via DiscordSRV.", False, 0),
            ("🗺️・dynmap-and-coords", "Community coordinates (Spawn, Nether Highway, End Portal, Trading Halls).", False, 0),
            ("🏰・hall-factions", "Hostel settlements, inter-hall diplomacy, trade alliances, and bases.", False, 0),
            ("💰・campus-marketplace", "Buy, sell, and trade items, ores, enchanted books, and materials.", False, 5),
            ("📸・build-showcase", "Share screenshots of your bases, megastructures, and campus replicas.", False, 5),
            ("⚡・redstone-and-farms", "Iron farms, raid farms, slime tech, and lag-optimization discussion.", False, 0),
            ("🏆・events-and-tourneys", "Dragon fight raids, build battles, and BedWars/PvP nights.", False, 0),
        ],
        "voice": []
    },
    "💬 ── CAMPUS HANGOUT ──": {
        "text": [
            ("💬・general-chat", "General discussions, campus talk, and chill vibes.", False, 3),
            ("🎮・other-games", "Valorant, CS2, BGMI, Chess, and coop gaming sessions.", False, 0),
            ("🤖・bot-commands", "Spam bot commands, music commands, and check stats here.", False, 5),
            ("💡・suggestions-and-polls", "Submit server feature suggestions, voting on datapacks/mods.", False, 0),
        ],
        "voice": []
    },
    "🆘 ── SUPPORT & TICKETS ──": {
        "text": [
            ("🎫・create-a-ticket", "Open private tickets for grief rollbacks, theft investigations, or bugs.", True, 0),
        ],
        "voice": []
    },
    "🔊 ── VOICE CHANNELS ──": {
        "text": [],
        "voice": [
            ("🔊・Lobby VC", 0),
            ("⛏️・Mining & Grinding", 2),
            ("🏰・Hall Squad", 4),
            ("⚡・Redstone Lab (Stream)", 6),
            ("🎵・Music & Chill", 0),
            ("➕・Create Temp VC", 0),
        ]
    },
    "🛡️ ── STAFF COMMAND ──": {
        "staff_only": True,
        "text": [
            ("🛡️・staff-chat", "Staff discussions and mod coordination.", False, 0),
            ("📋・whitelist-review", "Incoming player whitelist applications for staff review.", False, 0),
            ("📋・console-and-logs", "RCON logs, griefing warnings, whitelist automation log.", True, 0),
        ],
        "voice": [
            ("🔊・Staff Meeting Room", 0)
        ]
    }
}

# ==============================================================================
# INTERACTIVE DISCORD UI COMPONENTS
# ==============================================================================

class HallSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=hall, description=f"Join the {hall} Faction", emoji="🏰")
            for hall in HALL_ROLES
        ]
        super().__init__(
            placeholder="🏰 Select your Hostel / Hall...",
            min_values=0,
            max_values=1,
            options=options,
            custom_id="iitk_mc_hall_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        
        for hall_name in HALL_ROLES:
            h_role = discord.utils.get(guild.roles, name=hall_name)
            if h_role and h_role in member.roles:
                await member.remove_roles(h_role)

        if len(self.values) == 0:
            await interaction.response.send_message("Cleared your Hostel role.", ephemeral=True)
            return

        chosen = self.values[0]
        role = discord.utils.get(guild.roles, name=chosen)
        if role:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ You've been assigned **{chosen}**!", ephemeral=True)
        else:
            await interaction.response.send_message("Role not found on server.", ephemeral=True)


class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HallSelect())

    async def toggle_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(f"Role `{role_name}` not found.", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed role **{role_name}**.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added role **{role_name}**!", ephemeral=True)

    @discord.ui.button(label="Java Edition", style=discord.ButtonStyle.primary, emoji="💻", custom_id="role_btn_java")
    async def java_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "💻 Java Edition")

    @discord.ui.button(label="Bedrock / PE", style=discord.ButtonStyle.primary, emoji="📱", custom_id="role_btn_bedrock")
    async def bedrock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "📱 Bedrock / PE")

    @discord.ui.button(label="Redstone Tech", style=discord.ButtonStyle.secondary, emoji="⚡", custom_id="role_btn_redstone")
    async def redstone_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "⚡ Redstone Engineer")

    @discord.ui.button(label="Master Builder", style=discord.ButtonStyle.secondary, emoji="🎨", custom_id="role_btn_builder")
    async def builder_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "🎨 Master Builder")

    @discord.ui.button(label="Event Pings", style=discord.ButtonStyle.success, emoji="📢", custom_id="role_btn_events")
    async def events_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "📢 Event Pings")

    @discord.ui.button(label="Server Restarts", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="role_btn_restarts")
    async def restarts_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "⚠️ Server Restarts")


class WhitelistModal(discord.ui.Modal, title="⛏️ IITK Minecraft Whitelist Form"):
    ign = discord.ui.TextInput(
        label="Minecraft In-Game Name (IGN)",
        placeholder="e.g. Steve_IITK",
        required=True,
        min_length=3,
        max_length=24
    )
    edition = discord.ui.TextInput(
        label="Edition (Java or Bedrock)",
        placeholder="Java or Bedrock",
        required=True,
        max_length=10
    )
    roll_no = discord.ui.TextInput(
        label="IITK Roll Number",
        placeholder="e.g. 210456",
        required=True,
        min_length=5,
        max_length=12
    )
    hostel = discord.ui.TextInput(
        label="Hall of Residence / Hostel",
        placeholder="e.g. Hall 3 / Hall 12",
        required=False,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        review_channel = discord.utils.get(guild.text_channels, name="📋・whitelist-review")
        if not review_channel:
            review_channel = discord.utils.get(guild.text_channels, name="📋・whitelist-requests")

        embed = discord.Embed(
            title="📥 New Whitelist Application Received",
            color=discord.Color.from_rgb(26, 188, 156),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 Discord User", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="⛏️ Minecraft IGN", value=f"`{self.ign.value.strip()}`", inline=True)
        embed.add_field(name="🎮 Edition", value=f"`{self.edition.value.strip().capitalize()}`", inline=True)
        embed.add_field(name="🎓 Roll Number", value=f"`{self.roll_no.value.strip()}`", inline=True)
        embed.add_field(name="🏰 Hostel / Hall", value=f"`{self.hostel.value.strip() or 'N/A'}`", inline=True)
        embed.set_footer(text="Staff: Click below to approve or deny this request.")

        view = WhitelistApprovalView(applicant_id=interaction.user.id, ign=self.ign.value.strip())
        if review_channel:
            await review_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ **Application submitted!** Staff will review your whitelist request for **`{self.ign.value.strip()}`** shortly.",
            ephemeral=True
        )


class WhitelistApprovalView(discord.ui.View):
    def __init__(self, applicant_id: int, ign: str):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.ign = ign

    @discord.ui.button(label="Approve & Whitelist", style=discord.ButtonStyle.success, emoji="✅", custom_id="wl_approve")
    async def approve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        is_staff = any(r.name in ["👑 Server Admin / OP", "🛡️ Moderator", "⚙️ SysAdmin / Host"] for r in interaction.user.roles)
        if not (is_staff or interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("⛔ Only staff can approve whitelist requests.", ephemeral=True)
            return

        member = guild.get_member(self.applicant_id)
        if member:
            wl_role = discord.utils.get(guild.roles, name="⛏️ SMP Whitelisted")
            verified_role = discord.utils.get(guild.roles, name="🎓 Verified IITKian")
            if wl_role:
                await member.add_roles(wl_role)
            if verified_role:
                await member.add_roles(verified_role)

            try:
                await member.send(
                    f"🎉 **You have been whitelisted on IITK Minecraft!**\n"
                    f"Your IGN **`{self.ign}`** is approved. Check `#server-ip-and-guide` for connection details!"
                )
            except Exception:
                pass

        for item in self.children:
            item.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = f"✅ Whitelist Approved by {interaction.user.display_name}"
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"Whitelisted `{self.ign}` and assigned roles.", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, emoji="❌", custom_id="wl_reject")
    async def reject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_staff = any(r.name in ["👑 Server Admin / OP", "🛡️ Moderator", "⚙️ SysAdmin / Host"] for r in interaction.user.roles)
        if not (is_staff or interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("⛔ Only staff can reject requests.", ephemeral=True)
            return

        for item in self.children:
            item.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = f"❌ Whitelist Denied by {interaction.user.display_name}"
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"Rejected request for `{self.ign}`.", ephemeral=True)


class WhitelistLandingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Whitelist", style=discord.ButtonStyle.success, emoji="📝", custom_id="open_wl_modal")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WhitelistModal())


class TicketLauncher(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Report Grief / Theft", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="ticket_grief")
    async def grief_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_thread(interaction, "🚨 Griefing & Theft Report")

    @discord.ui.button(label="Bug or Lag Issue", style=discord.ButtonStyle.secondary, emoji="🐛", custom_id="ticket_bug")
    async def bug_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_thread(interaction, "🐛 Bug / Lag Report")

    @discord.ui.button(label="General Inquiries", style=discord.ButtonStyle.primary, emoji="❓", custom_id="ticket_general")
    async def help_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_thread(interaction, "❓ General Inquiry")

    async def create_ticket_thread(self, interaction: discord.Interaction, category_title: str):
        channel = interaction.channel
        user = interaction.user
        thread_name = f"ticket-{user.name[:10]}-{category_title.split()[1].lower()}"

        try:
            thread = await channel.create_thread(
                name=thread_name,
                type=discord.ChannelType.private_thread if interaction.guild.features and "PRIVATE_THREADS" in interaction.guild.features else discord.ChannelType.public_thread,
                auto_archive_duration=1440,
                reason=f"Support ticket opened by {user}"
            )
            await thread.add_user(user)
            
            mod_role = discord.utils.get(interaction.guild.roles, name="🛡️ Moderator")
            mod_mention = mod_role.mention if mod_role else "Staff"

            ticket_embed = discord.Embed(
                title=f"{category_title}",
                description=(
                    f"Hello {user.mention}! Welcome to your support ticket.\n\n"
                    f"**Please provide the following details:**\n"
                    f"• In-Game Name (IGN)\n"
                    f"• Coordinates of the incident (X, Y, Z)\n"
                    f"• Approximate time when it occurred\n"
                    f"• Screenshots or details\n\n"
                    f"A member of {mod_mention} will inspect via CoreProtect and assist shortly!"
                ),
                color=discord.Color.from_rgb(231, 76, 60)
            )
            await thread.send(embed=ticket_embed)
            await interaction.response.send_message(f"✅ Ticket created! Please head over to {thread.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to create ticket: {e}", ephemeral=True)


# ==============================================================================
# DISCORD COMMANDS (SLASH & PREFIX)
# ==============================================================================

@bot.tree.command(name="help", description="Show all IITK Minecraft server features and bot commands")
async def cmd_slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏰 IITK Minecraft Server Guide & Commands",
        description="Welcome! Here is everything you can do with the bot and the server:",
        color=discord.Color.from_rgb(33, 150, 243)
    )
    embed.add_field(
        name="📌 Getting Started",
        value=(
            "• **Pick Roles:** Go to <#pick-your-roles> to choose your Hall/Hostel, Java/Bedrock edition, and notifications.\n"
            "• **Whitelist Access:** Head to <#whitelist-requests> and click `[📝 Apply for Whitelist]`.\n"
            "• **Need Help / Grief Report:** Open a private ticket in <#create-a-ticket>."
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Bot Commands",
        value=(
            "• `/ip` or `!iitk ip` — Get the current server IP, port, and connection manual.\n"
            "• `/coords` or `!iitk coords` — View community coordinates (Spawn, Nether Hub, End Portal).\n"
            "• `/rules` or `!iitk rules` — Quick recap of server guidelines & anti-grief policy.\n"
            "• `/ping` or `!iitk ping` — Check bot response latency.\n"
            "• `/help` or `!iitk help` — Show this help manual."
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ Staff Commands",
        value="• `/whitelist_add <user> <ign>` — Instantly approve & whitelist a member (Staff only).",
        inline=False
    )
    await interaction.response.send_message(embed=embed)


@bot.command(name="help")
async def cmd_text_help(ctx):
    embed = discord.Embed(
        title="🏰 IITK Minecraft Server Guide & Commands",
        description="Here is everything you can do with the bot and the server:",
        color=discord.Color.from_rgb(33, 150, 243)
    )
    embed.add_field(
        name="📌 Getting Started",
        value=(
            "• **Pick Roles:** Head to `#pick-your-roles` to choose your Hall and platform.\n"
            "• **Whitelist:** Go to `#whitelist-requests` and click `[📝 Apply for Whitelist]`.\n"
            "• **Support:** Open a ticket in `#create-a-ticket`."
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Available Commands",
        value=(
            "• `!iitk ip` or `/ip` — Server address and ports\n"
            "• `!iitk coords` or `/coords` — Key points of interest\n"
            "• `!iitk rules` or `/rules` — Server rules recap\n"
            "• `!iitk ping` or `/ping` — Check bot latency\n"
            "• `!iitk help` or `/help` — This help menu"
        ),
        inline=False
    )
    await ctx.send(embed=embed)


@bot.tree.command(name="ip", description="Get the server address, ports, and connection guide")
async def cmd_slash_ip(interaction: discord.Interaction):
    ip_display = SERVER_IP if SERVER_IP else "Campus LAN IP (172.x.x.x) or Playit Tunnel"
    embed = discord.Embed(
        title="🌐 IITK Minecraft Connection Info",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="💻 Java Edition", value=f"Address: `{ip_display}`\nPort: `25565`\nVersion: `1.20.x / 1.21.x`", inline=False)
    embed.add_field(name="📱 Bedrock / PE", value=f"Address: `{ip_display}`\nPort: `19132`", inline=False)
    embed.add_field(name="🏫 Campus Note", value="Works directly on hostel Wi-Fi/LAN. Check <#announcements> for remote tunnels.", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.command(name="ip")
async def cmd_text_ip(ctx):
    ip_display = SERVER_IP if SERVER_IP else "Campus LAN IP (172.x.x.x) or Playit Tunnel"
    embed = discord.Embed(
        title="🌐 IITK Minecraft Connection Info",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="💻 Java Edition", value=f"Address: `{ip_display}`\nPort: `25565`\nVersion: `1.20.x / 1.21.x`", inline=False)
    embed.add_field(name="📱 Bedrock / PE", value=f"Address: `{ip_display}`\nPort: `19132`", inline=False)
    await ctx.send(embed=embed)


@bot.tree.command(name="coords", description="View key community locations and coordinates")
async def cmd_slash_coords(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🗺️ Community Points of Interest",
        description="Coordinates for key landmarks across the world:",
        color=discord.Color.from_rgb(241, 196, 15)
    )
    embed.add_field(name="🏛️ World Spawn", value="`X: 0, Y: 70, Z: 0`", inline=True)
    embed.add_field(name="🚇 Nether Hub", value="`X: 0, Y: 120, Z: 0` *(Nether)*", inline=True)
    embed.add_field(name="💰 Marketplace", value="Check <#campus-marketplace>", inline=True)
    embed.add_field(name="🐉 End Portal", value="Check <#dynmap-and-coords>", inline=True)
    embed.add_field(name="🏰 Hall Settlements", value="Declared in <#hall-factions>", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.command(name="coords")
async def cmd_text_coords(ctx):
    embed = discord.Embed(
        title="🗺️ Community Points of Interest",
        color=discord.Color.from_rgb(241, 196, 15)
    )
    embed.add_field(name="🏛️ World Spawn", value="`X: 0, Y: 70, Z: 0`", inline=True)
    embed.add_field(name="🚇 Nether Hub", value="`X: 0, Y: 120, Z: 0` *(Nether)*", inline=True)
    embed.add_field(name="💰 Marketplace", value="Check `#campus-marketplace`", inline=True)
    await ctx.send(embed=embed)


@bot.tree.command(name="rules", description="Quick overview of server rules & anti-grief policy")
async def cmd_slash_rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Server Rules & Guidelines Summary",
        description="1. **No Griefing / Stealing:** CoreProtect is active and logs all block & chest edits.\n2. **No Unfair Advantages:** No X-Ray, baritone, or hacked clients.\n3. **Campus Honor Code:** Respect fellow students in chat and voice.\n4. **Farms:** Keep farms lag-friendly with an off-switch.\n\nFull details in <#rules-and-conduct>.",
        color=discord.Color.from_rgb(33, 150, 243)
    )
    await interaction.response.send_message(embed=embed)


@bot.command(name="rules")
async def cmd_text_rules(ctx):
    await ctx.send("📜 Check out `#rules-and-conduct` for the complete rules and anti-grief policy!")


@bot.tree.command(name="ping", description="Check bot latency")
async def cmd_slash_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: `{latency}ms`")


@bot.command(name="ping")
async def cmd_text_ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: `{latency}ms`")


@bot.tree.command(name="whitelist_add", description="Staff: Manually whitelist a player")
async def cmd_slash_whitelist_add(interaction: discord.Interaction, member: discord.Member, ign: str):
    is_staff = any(r.name in ["👑 Server Admin / OP", "🛡️ Moderator", "⚙️ SysAdmin / Host"] for r in interaction.user.roles)
    if not (is_staff or interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Only staff can use this command.", ephemeral=True)
        return

    wl_role = discord.utils.get(interaction.guild.roles, name="⛏️ SMP Whitelisted")
    verified_role = discord.utils.get(interaction.guild.roles, name="🎓 Verified IITKian")
    if wl_role:
        await member.add_roles(wl_role)
    if verified_role:
        await member.add_roles(verified_role)

    try:
        await member.send(f"🎉 You have been whitelisted on IITK Minecraft as **`{ign}`**! Check `#server-ip-and-guide` for IP.")
    except Exception:
        pass

    await interaction.response.send_message(f"✅ Whitelisted {member.mention} as **`{ign}`**.")


# ==============================================================================
# DISCORD EVENTS & ARCHITECT ROUTINES
# ==============================================================================

@bot.event
async def on_ready():
    print("=" * 68, flush=True)
    print(f"🚀 IITK Minecraft Bot online as: {bot.user} (ID: {bot.user.id})", flush=True)
    print(f"📡 Connected to {len(bot.guilds)} server(s)", flush=True)
    print("=" * 68, flush=True)

    bot.add_view(RolesView())
    bot.add_view(WhitelistLandingView())
    bot.add_view(TicketLauncher())

    try:
        synced = await bot.tree.sync()
        print(f"⚡ Synced {len(synced)} slash command(s) successfully!", flush=True)
    except Exception as e:
        print(f"Slash command sync error: {e}", flush=True)

    for guild in bot.guilds:
        await setup_iitk_server(guild)

    print("🎉 Server architecture synced and listening for interactions!", flush=True)


async def setup_iitk_server(guild: discord.Guild):
    everyone = guild.default_role

    # 1. Sync Roles
    for role_info in reversed(ROLES_SPEC):
        existing = discord.utils.get(guild.roles, name=role_info["name"])
        if not existing:
            try:
                await guild.create_role(
                    name=role_info["name"],
                    color=role_info["color"],
                    hoist=role_info["hoist"],
                    mentionable=role_info["mentionable"]
                )
            except Exception:
                pass

    for hall in HALL_ROLES:
        existing = discord.utils.get(guild.roles, name=hall)
        if not existing:
            try:
                await guild.create_role(name=hall, color=discord.Color.from_rgb(120, 144, 156), hoist=False)
            except Exception:
                pass

    admin_role = discord.utils.get(guild.roles, name="👑 Server Admin / OP")
    mod_role = discord.utils.get(guild.roles, name="🛡️ Moderator")

    # 2. Sync Categories & Channels
    for cat_name, cat_data in STRUCTURE.items():
        is_staff_only = cat_data.get("staff_only", False)
        
        cat_overwrites = {
            everyone: discord.PermissionOverwrite(read_messages=True, connect=True)
        }
        if is_staff_only:
            cat_overwrites[everyone] = discord.PermissionOverwrite(read_messages=False, connect=False)
            if admin_role:
                cat_overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True)
            if mod_role:
                cat_overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True)

        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if not existing_cat:
            category = await guild.create_category(cat_name, overwrites=cat_overwrites)
        else:
            category = existing_cat
            await category.edit(overwrites=cat_overwrites)

        # Text Channels
        for ch_tuple in cat_data.get("text", []):
            ch_name, ch_topic, is_readonly, slowmode = ch_tuple
            existing_ch = discord.utils.get(guild.text_channels, name=ch_name)
            
            ch_overwrites = {
                everyone: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=False if is_readonly else True,
                    create_public_threads=False if is_readonly else True,
                    add_reactions=True
                )
            }
            if is_readonly:
                if admin_role:
                    ch_overwrites[admin_role] = discord.PermissionOverwrite(send_messages=True)
                if mod_role:
                    ch_overwrites[mod_role] = discord.PermissionOverwrite(send_messages=True)

            if not existing_ch:
                await category.create_text_channel(
                    name=ch_name,
                    topic=ch_topic,
                    overwrites=ch_overwrites,
                    slowmode_delay=slowmode
                )
            else:
                await existing_ch.edit(category=category, topic=ch_topic, slowmode_delay=slowmode)
                if is_readonly:
                    await existing_ch.set_permissions(everyone, send_messages=False)

        # Voice Channels
        for vc_name, limit in cat_data.get("voice", []):
            existing_vc = discord.utils.get(guild.voice_channels, name=vc_name)
            if not existing_vc:
                await category.create_voice_channel(name=vc_name, user_limit=limit or 0)
            else:
                await existing_vc.edit(category=category, user_limit=limit or 0)

    # Clean up deprecated channels/categories
    for old_name in ["🏰・Hall Squad 1", "🏰・Hall Squad 2"]:
        old_vc = discord.utils.get(guild.voice_channels, name=old_name)
        if old_vc:
            try:
                await old_vc.delete()
            except Exception:
                pass

    stats_cat = discord.utils.get(guild.categories, name="📊 ── SERVER STATS ──")
    if stats_cat:
        try:
            for ch in stats_cat.channels:
                await ch.delete()
            await stats_cat.delete()
        except Exception:
            pass

    # 3. Deploy Interactive Embeds
    await deploy_master_panels(guild)


async def deploy_master_panels(guild: discord.Guild):
    # Rules Embed
    rules_channel = discord.utils.get(guild.text_channels, name="📜・rules-and-conduct")
    if rules_channel:
        history = [msg async for msg in rules_channel.history(limit=5)]
        if len(history) == 0:
            embed = discord.Embed(
                title="🏰 IITK Minecraft SMP • Official Server Guidelines",
                description=(
                    "Welcome to the official **IIT Kanpur Minecraft SMP & Community Server**!\n\n"
                    "We are dedicated to building a welcoming, creative, and healthy gaming environment "
                    "for students across all halls, departments, and batches. "
                    "By participating in this server, you agree to adhere to the code of conduct below.\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.from_rgb(33, 150, 243)
            )
            embed.add_field(
                name="1️⃣ Zero-Tolerance Griefing & Theft Policy",
                value=(
                    "• Destroying, altering, or defacing other players' builds is strictly forbidden.\n"
                    "• Unauthorized opening and looting of containers/chests is treated as theft.\n"
                    "• **CoreProtect 21+** is active: Every block placement, break, container transaction, "
                    "and interaction is logged with timestamps and player IGNs."
                ),
                inline=False
            )
            embed.add_field(
                name="2️⃣ Fair Play & Integrity (No Unfair Advantages)",
                value=(
                    "• **Prohibited:** X-Ray packs, Baritone, auto-clickers, fly hacks, and any modified clients providing an unfair advantage.\n"
                    "• **Allowed Client Mods:** Sodium, Lithium, Iris, OptiFine, MiniHUD, JourneyMap (with radar disabled), Litematica (easy-place disabled)."
                ),
                inline=False
            )
            embed.add_field(
                name="3️⃣ IITK Campus Honor Code",
                value=(
                    "• Treat fellow crafters with respect in Discord channels, in-game chat, and voice rooms.\n"
                    "• Toxic behavior, harassment, hate speech, or sharing personal room/roll details without consent will lead to immediate bans."
                ),
                inline=False
            )
            embed.add_field(
                name="4️⃣ Technical Redstone & Farm Etiquette",
                value=(
                    "• Always design high-output farms with an accessible **Off-Switch**.\n"
                    "• Keep persistent hopper timers and mob entities within sensible limits so server MSPT stays under 40ms (20 TPS)."
                ),
                inline=False
            )
            embed.add_field(
                name="5️⃣ Hall Factions & Friendly Rivalry",
                value=(
                    "• Inter-hall banter and friendly competition are celebrated!\n"
                    "• Formal wars, PvP challenges, and territory disputes must be mutually agreed upon in <#hall-factions>."
                ),
                inline=False
            )
            embed.set_footer(text="IITK Minecraft Network • Maintained by students for students • Play Fair & Have Fun")
            await rules_channel.send(embed=embed)

    # Server IP Guide
    guide_channel = discord.utils.get(guild.text_channels, name="🌐・server-ip-and-guide")
    if guide_channel:
        history = [msg async for msg in guide_channel.history(limit=5)]
        if len(history) == 0:
            ip_display = SERVER_IP if SERVER_IP else "Campus LAN IP (e.g. 172.x.x.x / Playit.gg tunnel)"
            embed = discord.Embed(
                title="🌐 IITK Minecraft Connection Manual & Server Specs",
                description="Everything you need to connect to the campus server from hostels or remotely.",
                color=discord.Color.from_rgb(46, 204, 113)
            )
            embed.add_field(
                name="💻 Java Edition (PC / Mac / Linux)",
                value=(
                    f"**Server Address:** `{ip_display}`\n"
                    "**Default Port:** `25565`\n"
                    "**Supported Versions:** `1.20.x` through `1.21.x`"
                ),
                inline=False
            )
            embed.add_field(
                name="📱 Bedrock / Mobile Crossplay (GeyserMC + Floodgate)",
                value=(
                    f"**Server Address:** `{ip_display}`\n"
                    "**Bedrock Port:** `19132`\n"
                    "*(Play on Android, iOS, Windows 10/11, Nintendo Switch, PS5, Xbox!)*"
                ),
                inline=False
            )
            embed.add_field(
                name="🏫 Campus Network Connection Options",
                value=(
                    "• **Hostel / Academic LAN:** Direct intranet connection with ultra-low ping (<2ms).\n"
                    "• **Remote / Off-Campus:** Connect via student VPN, Cloudflare Tunnel, or Playit.gg link posted in `#announcements`."
                ),
                inline=False
            )
            embed.set_footer(text="Need help joining? Open a ticket in #create-a-ticket")
            await guide_channel.send(embed=embed)

    # Roles View
    roles_channel = discord.utils.get(guild.text_channels, name="🎭・pick-your-roles")
    if roles_channel:
        history = [msg async for msg in roles_channel.history(limit=5)]
        if len(history) == 0:
            embed = discord.Embed(
                title="🎭 Customize Your Roles & Notifications",
                description=(
                    "Select your hostel, your Minecraft platform, and customize which pings you receive.\n\n"
                    "🏰 **Hostel Selection:** Pick your hall from the dropdown menu below.\n"
                    "💻 **Edition:** Click Java or Bedrock.\n"
                    "⚡ **Playstyle:** Claim your specialty (Redstone, Builder).\n"
                    "📢 **Notifications:** Opt-in to Event or Restart pings."
                ),
                color=discord.Color.from_rgb(155, 89, 182)
            )
            await roles_channel.send(embed=embed, view=RolesView())

    # Whitelist View
    wl_channel = discord.utils.get(guild.text_channels, name="📋・whitelist-requests")
    if wl_channel:
        history = [msg async for msg in wl_channel.history(limit=5)]
        if len(history) == 0:
            embed = discord.Embed(
                title="📋 Whitelist Application Portal",
                description=(
                    "To maintain a grief-free environment, access to the SMP requires whitelisting.\n\n"
                    "**Requirements:**\n"
                    "• Valid Minecraft Java or Bedrock username\n"
                    "• Active IITK Roll Number\n\n"
                    "Click the **Apply for Whitelist** button below to open the application modal. "
                    "Once approved, you will automatically receive the **⛏️ SMP Whitelisted** role!"
                ),
                color=discord.Color.from_rgb(26, 188, 156)
            )
            await wl_channel.send(embed=embed, view=WhitelistLandingView())

    # Ticket View
    ticket_channel = discord.utils.get(guild.text_channels, name="🎫・create-a-ticket")
    if ticket_channel:
        history = [msg async for msg in ticket_channel.history(limit=5)]
        if len(history) == 0:
            embed = discord.Embed(
                title="🆘 IITK Minecraft Helpdesk & Ticket Center",
                description=(
                    "Need assistance from staff? Have you encountered a griefing incident, lost items due to a bug, "
                    "or have a technical inquiry?\n\n"
                    "**Select a category below to open a private support thread:**\n"
                    "🚨 **Report Grief / Theft:** Request a CoreProtect investigation and block rollback.\n"
                    "🐛 **Bug or Lag Issue:** Report server lag spikes, stuck chunks, or broken mob caps.\n"
                    "❓ **General Inquiries:** Whitelist questions, faction claims, and suggestions."
                ),
                color=discord.Color.from_rgb(231, 76, 60)
            )
            await ticket_channel.send(embed=embed, view=TicketLauncher())


# ==============================================================================
# RENDER FREE TIER KEEP-ALIVE WEB SERVER
# ==============================================================================

async def handle_health_check(request):
    return web.Response(text="🟢 IITK Minecraft Discord Bot is Online & Healthy!", content_type="text/plain")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Keep-Alive Health HTTP Server running on port {PORT} (Render compatible)", flush=True)

async def main():
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable or command-line argument is missing!")
        sys.exit(1)

    # Run the keep-alive web server and the Discord bot together
    await start_web_server()
    await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
