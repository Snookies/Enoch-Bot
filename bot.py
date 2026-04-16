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

# Build a per-translation lookup of available verses
def build_verse_map(translation_key):
    verse_map = {}
    for ref in enoch_data["translations"][translation_key].keys():
        ch, vs = ref.split(":")
        ch = int(ch)
        vs = int(vs)
        verse_map.setdefault(ch, set()).add(vs)
    return verse_map

translation_verse_maps = {
    key: build_verse_map(key)
    for key in enoch_data["translations"]
}

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)
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
        "`/enoch reference:<chapter:verse[-verse]> translation:<version>` - Get passage from 1 Enoch\n"

    )
    await interaction.response.send_message(help_message)

# ----- /enoch  ----- 

@tree.command(name="enoch", description="Get a passage from 1 Enoch.")
@app_commands.describe(
    reference="Format: 48:1 or 48:1-10",
    translation="Choose a translation version"
)
@app_commands.choices(
    translation=[
        app_commands.Choice(name="Charlesworth (1983)", value="charlesworth"),
        app_commands.Choice(name="Hermeneia (2012)", value="hermeneia")
    ]
)
async def slash_enoch(
    interaction: discord.Interaction,
    reference: str,
    translation: app_commands.Choice[str]
):
    try:
        reference = reference.replace(" ", "")
        version = translation.value

        text_data = enoch_data["translations"].get(version)
        if not text_data:
            await interaction.response.send_message("❌ Translation not found.", ephemeral=True)
            return

        chapter_verse_map = translation_verse_maps[version]

        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')

            if not chapter.isdigit() or not start_verse.isdigit() or not end_verse.isdigit():
                await interaction.response.send_message("❌ Invalid format. Use chapter:verse or chapter:verse-verse.", ephemeral=True)
                return

            chapter_num = int(chapter)
            start = int(start_verse)
            end = int(end_verse)

            if start > end:
                await interaction.response.send_message("❌ Invalid range: start must be <= end.", ephemeral=True)
                return

            if chapter_num not in chapter_verse_map:
                await interaction.response.send_message("❌ Chapter not found.", ephemeral=True)
                return

            # Check that at least one verse in the range exists
            available_in_range = [v for v in range(start, end + 1) if v in chapter_verse_map[chapter_num]]
            if not available_in_range:
                await interaction.response.send_message(
                    f"❌ No verses found in {chapter}:{start}-{end} for this translation.",
                    ephemeral=True
                )
                return

            verses_text = ""
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = text_data.get(key)
                if verse_text:
                    verses_text += f"**{v}.** {verse_text}\n"
                # Silently skip merged/absent verses rather than showing [Not found]

            embed = discord.Embed(
                title=f"1 Enoch {chapter}:{start}-{end}",
                description=verses_text.strip(),
                color=discord.Color.gold()
            )
            embed.set_footer(text=translation.name)

            if len(embed.description) > 4096:
                await interaction.response.send_message("⚠️ Passage too long to display in a single embed.", ephemeral=True)
                return

            await interaction.response.send_message(embed=embed)

        else:
            chapter, verse = reference.split(':')

            if not chapter.isdigit() or not verse.isdigit():
                await interaction.response.send_message("❌ Invalid format. Use chapter:verse.", ephemeral=True)
                return

            chapter_num = int(chapter)
            verse_num = int(verse)

            if chapter_num not in chapter_verse_map or verse_num not in chapter_verse_map[chapter_num]:
                await interaction.response.send_message("❌ That verse does not exist.", ephemeral=True)
                return

            key = f"{chapter}:{verse}"
            verse_text = text_data.get(key)

            embed = discord.Embed(
                title=f"1 Enoch {key}",
                description=f"**{verse}.** {verse_text}",
                color=discord.Color.gold()
            )
            embed.set_footer(text=translation.name)
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)






# ----- Run the Bot -----

print("Starting bot...")
bot.run(TOKEN)
