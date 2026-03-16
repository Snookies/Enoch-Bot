# 📜 Enoch-Bot

A 1 Enoch bot for Discord

[Invite me to your server](https://discord.com/oauth2/authorize?client_id=1373346108637708549&permissions=0&integration_type=0&scope=bot+applications.commands)


## Features

- `/enoch` — Look up a verse or range of verses from 1 Enoch
- `/ping` — Check if the bot is online
- `/commands` — List available commands

**Supported translations:**
- Charlesworth (1983)
- Hermeneia (2012)

---
## Self-Hosting

### Prerequisites
- Python 3.10+
- A Discord bot token ([create one here](https://discord.com/developers/applications))

### Setup

1. **Clone the repo**
```bash
   git clone https://github.com/Snookies/Enoch-Bot.git
   cd Enoch-Bot
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Create a `.env` file** in the project root:
```
   DISCORD_TOKEN=your_token_here
```

4. **Run the bot**
```bash
   python bot.py
```

### Discord Bot Setup
When creating your bot in the Developer Portal, make sure to enable:
- `Message Content Intent` (under Bot → Privileged Gateway Intents)

---

## Deploying to a Host (Railway, Render, etc.)

A `Procfile` is included for platforms that support it:
```
worker: python bot.py
```

Set `DISCORD_TOKEN` as an environment variable in your host's dashboard instead of using a `.env` file.

---

## File Structure
```
Enoch-Bot/
├── bot.py               # Main bot code
├── enoch_texts.json     # Verse data for 1 Enoch
├── requirements.txt     # Python dependencies
├── Procfile             # For hosted deployment
├── .gitignore           # Excludes .env from git
└── README.md            # This file
```

---

## Usage Example
```
/enoch reference:48:1 translation:Charlesworth (1983)
/enoch reference:48:1-10 translation:Hermeneia (2012)
```

---


## Bibliography
Charlesworth, James H., ed. *The Old Testament Pseudepigrapha Volume 1: Apocalyptic Literature and Testaments*. Garden City, New York: Doubleday & Company, Inc, 1983.

Nickelsburg, George W. E., and James C. VanderKam, eds. *1 Enoch: The Hermeneia Translation*. Minneapolis: Fortress Press, 2012.

