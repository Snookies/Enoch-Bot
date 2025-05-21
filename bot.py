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
        output = ""

        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')
            start = int(start_verse)
            end = int(end_verse)

            verses = []
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key)
                if verse_text:
                    verses.append(f"**{v}.** {verse_text}")

            if verses:
                joined_verses = " ".join(verses)
                output = f"**1 Enoch {chapter}:{start}-{end}**\n>>> {joined_verses}"
        else:
            verse_text = enoch_data["enoch"].get(reference)
            if verse_text:
                chapter, verse = reference.split(':')
                output = f"**1 Enoch {reference}**\n>>> **{verse}.** {verse_text}"

        if output:
            await ctx.send(output)
        else:
            await ctx.send("Verse not found.")

    except Exception as e:
        await ctx.send("An error occurred.")

# ----- Global Slash Commands -----

@tree.command(name="ping", description="Test if the bot is responsive.")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="commands", description="Show available commands.")
async def slash_help(interaction: discord.Interaction):
    help_message = (
        "**Available Slash Commands:**\n"
        "`/commands` - Show list of commands\n"
        "`/ping` - Test bot responsiveness\n"
        "`/enoch <reference>` - Get passage from 1 Enoch\n"
    )
    await interaction.response.send_message(help_message)

@tree.command(name="enoch", description="Get a passage from 1 Enoch.")
@app_commands.describe(reference="Format: 10:3 or 10:3-9")
async def slash_enoch(interaction: discord.Interaction, reference: str):
    try:
        output = ""
        reference = reference.replace(" ", "")  # Remove spaces to avoid format errors

        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')
            start = int(start_verse)
            end = int(end_verse)

            verses = []
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key)
                if verse_text:
                    verses.append(f"**{v}.** {verse_text}")

            if not verses:
                await interaction.response.send_message("No verses found for that range.", ephemeral=True)
                return

            # Chunk response into blocks under 2000 characters
            MAX_LENGTH = 1800
            chunks = []
            current = ""

            for verse in verses:
                if len(current) + len(verse) + 1 > MAX_LENGTH:
                    chunks.append(current)
                    current = ""
                current += verse + " "

            if current:
                chunks.append(current)

            # Send first chunk as initial response, the rest as follow-ups
            await interaction.response.send_message(
                f"**1 Enoch {chapter}:{start}-{end}**\n>>> {chunks[0]}"
            )
            for chunk in chunks[1:]:
                await interaction.followup.send(f">>> {chunk}")

        else:
            # Single verse
            chapter, verse = reference.split(':')
            key = f"{chapter}:{verse}"
            verse_text = enoch_data["enoch"].get(key)
            if verse_text:
                output = f"**1 Enoch {key}**\n>>> **{verse}.** {verse_text}"
                await interaction.response.send_message(output)
            else:
                await interaction.response.send_message("❌ Verse not found.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error while processing reference: {e}", ephemeral=True)

