import os
import json
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

ROLE_HEROES = {
    "Tank": ["Doomfist", "D.Va", "Ramattra", "Reinhardt", "Roadhog", "Sigma", "Winston", "Zarya"],
    "DPS": [
        "Ashe", "Bastion", "Cassidy", "Echo", "Freja", "Genji", "Hanzo", "Junkrat", "Mei",
        "Pharah", "Reaper", "Sojourn", "Soldier: 76", "Sombra", "Symmetra",
        "Torbjörn", "Tracer", "Venture", "Widowmaker"
    ],
    "Support": [
        "Ana", "Baptiste", "Brigitte", "Illari", "Kiriko",
        "Lifeweaver", "Lucio", "Mercy", "Moira", "Zenyatta"
    ]
}

GAMEMODE_MAPS = {
    "Control": ["Antarctic Peninsula", "Busan", "Ilios", "Lijiang Tower", "Nepal", "Oasis", "Samoa"],
    "Escort": ["Circuit Royal", "Dorado", "Havana", "Junkertown", "Rialto", "Route 66", "Shambali Monastery", "Watchpoint: Gibraltar"],
    "Push": ["New Queen Street", "Colosseo", "Esperança", "Runasapi"],
    "Hybrid": ["Blizzard World", "Eichenwalde", "Hollywood", "King's Row", "Midtown", "Numbani", "Paraíso"],
    "Flashpoint": ["New Junk City", "Suravasa"]
}

RANKS = [
    "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master",
    "Grandmaster", "Top 500", "GM 1", "GM 2", "GM 3"
]

ALL_HEROES = [hero for heroes in ROLE_HEROES.values() for hero in heroes]
ALL_MAPS = [m for maps in GAMEMODE_MAPS.values() for m in maps]


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
        reference = reference.replace(" ", "")
        embed = None

        if '-' in reference:
            chapter_verse, end_verse = reference.split('-')
            chapter, start_verse = chapter_verse.split(':')
            start = int(start_verse)
            end = int(end_verse)

            verses_text = ""
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key)
                if verse_text:
                    verses_text += f"**{v}.** {verse_text}\n"

            if not verses_text:
                await ctx.send("❌ No verses found for that range.")
                return

            embed = discord.Embed(
                title=f"1 Enoch {chapter}:{start}-{end}",
                description=verses_text.strip(),
                color=discord.Color.gold()
            )

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
            else:
                await ctx.send("❌ Verse not found.")
                return

        if embed and len(embed.description) <= 4096:
            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Passage too long to display in a single embed.")

    except Exception as e:
        await ctx.send("⚠️ An error occurred.")



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

            verses_text = ""
            for v in range(start, end + 1):
                key = f"{chapter}:{v}"
                verse_text = enoch_data["enoch"].get(key)
                if verse_text:
                    verses_text += f"**{v}.** {verse_text}\n"

            if not verses_text:
                await interaction.response.send_message("❌ No verses found for that range.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"1 Enoch {chapter}:{start}-{end}",
                description=verses_text.strip(),
                color=discord.Color.gold()
            )

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
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("❌ Verse not found.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

# -------- OVERWATCH -----------

@bot.tree.command(name="matchinfo", description="Log an Overwatch match")
@app_commands.describe(
    hero="Hero you played",
    map_name="Map you played on",
    rank="Your current rank",
    result="Match result"
)
@app_commands.choices(
    hero=[app_commands.Choice(name=h, value=h) for h in sorted(ALL_HEROES)],
    map_name=[app_commands.Choice(name=m, value=m) for m in sorted(ALL_MAPS)],
    rank=[app_commands.Choice(name=r, value=r) for r in RANKS],
    result=[
        app_commands.Choice(name="Win", value="Win"),
        app_commands.Choice(name="Loss", value="Loss")
    ]
)
async def matchinfo(
    interaction: discord.Interaction,
    hero: app_commands.Choice[str],
    map_name: app_commands.Choice[str],
    rank: app_commands.Choice[str],
    result: app_commands.Choice[str]
):
    # Find role from hero
    role = next((r for r, heroes in ROLE_HEROES.items() if hero.value in heroes), "Unknown")

    table = (
        f"{'Hero(s)':<20}{'Role':<10}{'Map':<22}{'Rank':<10}{'Result':<10}\n"
        f"{'-'*20}{'-'*10}{'-'*22}{'-'*10}{'-'*10}\n"
        f"{hero.value:<20}{role:<10}{map_name.value:<22}{rank.value:<10}{result.value:<10}"
    )

    embed = discord.Embed(
        title="Match Information",
        description=f"```{table}```",
        color=discord.Color.green() if result.value == "Win" else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)





# ----- Run the Bot -----

print("Starting bot...")
bot.run(TOKEN)
