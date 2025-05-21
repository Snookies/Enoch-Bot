import os
import json
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands



# Load the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Load Enoch JSON file
with open("enoch_texts.json", "r", encoding="utf-8") as f:
    enoch_data = json.load(f)

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree  # For slash commands

# Event: bot is ready
@bot.event
async def on_ready():
    # Optional: Clear and re-sync global slash commands
    try:
        await tree.sync()
        print(f"Logged in as {bot.user} and slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# ----- Prefix Commands -----

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="commands")
async def custom_help(ctx):
    help_message = (
        "**Available Commands:** \n"
        "`!commands` - Show list of commands\n"
        "`/ping` - Test bot responsiveness\n"
        "`!enoch <chapter:verse>` or `<chapter:verse-verse>` - Get passage from 1 Enoch\n"
    )
    await ctx.send(help_message)

@bot.command()
async def enoch(ctx, reference: str):
    try:
        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')
            start = int(start_verse)
            end = int(end_verse)

            embed = discord.Embed(
                title=f"1 Enoch {chapter}:{start}-{end}",
                color=discord.Color.gold()
            )

            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key, "[Not found]")
                # Add each verse as a field
                embed.add_field(name=f"Verse {v}", value=verse_text, inline=False)

            # embed.set_footer(text="From 1 Enoch")
            await ctx.send(embed=embed)

        else:
            chapter, verse = reference.split(':')
            key = f"{chapter}:{verse}"
            verse_text = enoch_data["enoch"].get(key)
            if verse_text:
                embed = discord.Embed(
                    title=f"1 Enoch {key}",
                    description=f"**{verse}.** {verse_text}",
                    color=discord.Color.gold()
                )
                embed.set_footer(text="From 1 Enoch")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Verse not found.")

    except Exception as e:
        await ctx.send("An error occurred.")


# ----- Global Slash Commands -----

# ----- /ping -----

@tree.command(name="ping", description="Test if the bot is responsive.")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# ----- /commands -----

@tree.command(name="commands", description="Show available commands.")
async def slash_help(interaction: discord.Interaction):
    help_message = (
        "**Available Slash Commands:**\n"
        "`/commands` - Show list of commands\n"
        "`/ping` - Test bot responsiveness\n"
        "`/enoch <reference>` - Get passage from 1 Enoch\n"
    )
    await interaction.response.send_message(help_message)

# ----- /enoch  ----- 

@tree.command(name="enoch", description="Get a passage from 1 Enoch.")
@app_commands.describe(reference="Format: 48:1 or 48:1-10")
async def slash_enoch(interaction: discord.Interaction, reference: str):
    try:
        reference = reference.replace(" ", "")

        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')
            start = int(start_verse)
            end = int(end_verse)

            # Build one big string for description with all verses concatenated
            verses_text = ""
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key, "[Not found]")
                verses_text += f"**{v}.** {verse_text} "

            embed = discord.Embed(
                title=f"1 Enoch {chapter}:{start}-{end}",
                description=verses_text.strip(),
                color=discord.Color.gold()
            )

            embed.set_footer(text="From 1 Enoch")

            if len(embed.description) > 4096:
                await interaction.response.send_message(
                    "⚠️ Passage too long to display in a single embed.", ephemeral=True
                )
                return

            await interaction.response.send_message(embed=embed)

        else:
            chapter, verse = reference.split(':')
            key = f"{chapter}:{verse}"
            verse_text = enoch_data["enoch"].get(key)
            if verse_text:
                embed = discord.Embed(
                    title=f"1 Enoch {key}",
                    description=f"**{verse}.** {verse_text}",
                    color=discord.Color.gold()
                )
                embed.set_footer(text="From 1 Enoch")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("❌ Verse not found.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)






# ----- Run the Bot -----

print("Starting bot...")
bot.run(TOKEN)
