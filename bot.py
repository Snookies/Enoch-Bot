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

@tree.command(name="matchinfo", description="Record a match result with role, heroes, map, rank and result")
@app_commands.describe(
    role="Choose the role played",
    heroes="Comma separated heroes (must belong to chosen role)",
    gamemode="Choose the game mode",
    map_name="Choose the map played",
    rank="Your rank (free text)",
    result="Match result"
)
@app_commands.choices(
    role=[
        app_commands.Choice(name="Tank", value="Tank"),
        app_commands.Choice(name="DPS", value="DPS"),
        app_commands.Choice(name="Support", value="Support"),
    ],
    gamemode=[
        app_commands.Choice(name=k, value=k) for k in GAMEMODE_MAPS.keys()
    ],
    result=[
        app_commands.Choice(name="Win", value="Win"),
        app_commands.Choice(name="Loss", value="Loss")
    ]
)
async def matchinfo(
    interaction: discord.Interaction,
    role: app_commands.Choice[str],
    heroes: str,
    gamemode: app_commands.Choice[str],
    map_name: str,
    rank: str,
    result: app_commands.Choice[str]
):
    # Normalize inputs
    hero_list = [h.strip() for h in heroes.split(",")]

    # Validate heroes vs role
    valid_heroes = ROLE_HEROES.get(role.value, [])
    invalid_heroes = [h for h in hero_list if h not in valid_heroes]

    if invalid_heroes:
        await interaction.response.send_message(
            f"❌ The following hero(es) are invalid for role {role.value}: {', '.join(invalid_heroes)}",
            ephemeral=True
        )
        return

    # Validate map vs gamemode
    valid_maps = GAMEMODE_MAPS.get(gamemode.value, [])
    if map_name not in valid_maps:
        await interaction.response.send_message(
            f"❌ Invalid map for game mode {gamemode.value}. Valid maps are: {', '.join(valid_maps)}",
            ephemeral=True
        )
        return

    # Format table string
    # Ensure column widths roughly consistent, truncate if needed
    heroes_str = ", ".join(hero_list)
    table = (
        "Hero(s)       | Role    | Map                  | Rank     | Result\n"
        "------------- | ------- | -------------------- | -------- | ------\n"
        f"{heroes_str:<13} | {role.value:<7} | {map_name:<20} | {rank:<8} | {result.value}"
    )

    embed = discord.Embed(
        title="Match Information",
        description=f"```ansi\n{table}```",
        color=discord.Color.green() if result.value == "Win" else discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)




# ----- Run the Bot -----

print("Starting bot...")
bot.run(TOKEN)
