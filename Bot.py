import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Channel IDs
SCAM_ALERTS_CHANNEL_ID = 1348157361801662485  # Live-scam-alerts
TICKET_LOGS_CHANNEL_ID = 1348226135468802131  # Ticket logs

# ✅ Dictionary to store ticket -> scammer mapping
ticket_scammer_map = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot and message.channel.name.startswith("ticket-"):  
        print(f'🎟️ Ticket Created in {message.channel.name}')
        print(f"📝 Message Content: {message.content}")  # Debugging

        scammer_username = None
        platform_game = None
        ticket_creator = None  # Stores the user who created the ticket

        # ✅ Extract Ticket Creator (First Tagged User)
        if message.mentions:
            ticket_creator = message.mentions[0].mention  # Gets the first tagged user
            print(f"👤 Ticket Creator: {ticket_creator}")

        # ✅ Extract Scammer Info from Embed
        if message.embeds:
            for embed in message.embeds:
                embed_data = embed.to_dict()

                # ✅ Extract scammer's username and platform/game
                if embed_data.get("description"):
                    description = embed_data["description"]
                    print(f"🔍 Checking description: {description}")

                    if "**Scammer Username:**" in description:
                        scammer_username = description.split("**Scammer Username:**")[1].split("\n")[0].strip()
                        print(f"🎯 Extracted Scammer Username: {scammer_username}")

                    if "*Platform:*" in description or "*Game:*" in description:
                        platform_game = (
                            description.split("*Platform:*")[1].split("\n")[0].strip()
                            if "*Platform:*" in description else 
                            description.split("*Game:*")[1].split("\n")[0].strip()
                        )
                        print(f"🎯 Extracted Platform/Game: {platform_game}")

        # ✅ Store ticket data
        if scammer_username and platform_game and ticket_creator:
            ticket_scammer_map[message.channel.name] = (scammer_username, platform_game, ticket_creator)

            # ✅ Log to Ticket Logs Channel
            ticket_logs_channel = await bot.fetch_channel(TICKET_LOGS_CHANNEL_ID)
            if ticket_logs_channel:
                await ticket_logs_channel.send(
                    f"📄 **New Scam Report Logged**\n"
                    f"👤 **Reported by:** {ticket_creator}\n"
                    f"👤 **Scammer:** `{scammer_username}`\n"
                    f"🎮 **Platform/Game:** `{platform_game}`"
                )

            # ✅ Send Scam Alert
            scam_alerts_channel = await bot.fetch_channel(SCAM_ALERTS_CHANNEL_ID)
            if scam_alerts_channel:
                alert_message = (
                    f"🚨 **New Scam Report Created!** 🚨\n"
                    f"👤 **Reported by:** {ticket_creator}\n"
                    f"👤 **Scammer Username:** `{scammer_username}`\n"
                    f"🎮 **Platform/Game:** `{platform_game}`\n"
                    f"⚠️ Stay alert and report any further suspicious activity.\n"
                    f"———————"
                )
                print(f"✅ Sending Alert: {alert_message}")
                await scam_alerts_channel.send(alert_message)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
