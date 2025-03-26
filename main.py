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

# Dictionary to store ticket -> scammer mapping
ticket_scammer_map = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()  # Sync commands at startup

@bot.event
async def on_message(message):
    if message.author.bot and message.channel.name.startswith("ticket-"):
        scammer_username = None
        platform_game = None
        ticket_creator = None

        # Extract Ticket Creator (First Tagged User)
        if message.mentions:
            ticket_creator = message.mentions[0].mention

        # Extract Scammer Info from Embed
        if message.embeds:
            for embed in message.embeds:
                embed_data = embed.to_dict()
                
                if embed_data.get("description"):
                    description = embed_data["description"]
                    
                    if "**Scammer Username:**" in description:
                        scammer_username = description.split("**Scammer Username:**")[1].split("\n")[0].strip()
                    
                    if "*Platform:*" in description or "*Game:*" in description:
                        platform_game = (
                            description.split("*Platform:*")[1].split("\n")[0].strip()
                            if "*Platform:*" in description else 
                            description.split("*Game:*")[1].split("\n")[0].strip()
                        )

        # Store ticket data
        if scammer_username and platform_game and ticket_creator:
            ticket_scammer_map[message.channel.name] = (scammer_username, platform_game, ticket_creator)

            # Send Scam Alert
            scam_alerts_channel = await bot.fetch_channel(SCAM_ALERTS_CHANNEL_ID)
            if scam_alerts_channel:
                await scam_alerts_channel.send(
                    f"🚨 **New Scamper Report Created!** 🚨\n"
                    f"👤 **Reported by:** {ticket_creator}\n"
                    f"👤 **Scammer Username:** `{scammer_username}`\n"
                    f"🎮 **Platform/Game:** `{platform_game}`\n"
                    f"⚠️ Stay alert and report any further suspicious activity.\n"
                    f"———————"
                )

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def report(ctx, user: discord.Member, *, platform_game: str):
    scam_alerts_channel = await bot.fetch_channel(SCAM_ALERTS_CHANNEL_ID)
    if scam_alerts_channel:
        await scam_alerts_channel.send(
            f"🚨 **New Scamper Report Created!** 🚨\n"
            f"👤 **Reported by:** {ctx.author.mention}\n"
            f"👤 **Scammer Username:** `{user.name}`\n"
            f"🎮 **Platform/Game:** `{platform_game}`\n"
            f"⚠️ Stay alert and report any further suspicious activity.\n"
            f"———————"
        )

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
