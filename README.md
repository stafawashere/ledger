# Ledger Bot

A Discord bot for tracking balances, debts, and inventory — built with slash commands and an interactive UI.

## Features

- **Balance Management** — Manage a central ledger balance with add, subtract, and set operations
- **Debt Management** — Track associates and their debts with full history per person
- **Asset Inventory** — Track stock quantities with custom units, thumbnails, and settings
- **History Audits** — Automatic audit trail on every mutation with filtering and export

## Commands

| Command | Description |
|---------|-------------|
| `/ledger` | Overview of balance, owed, associates, assets, and recent history |
| `/wipe` | Reset all data with confirmation prompt |
| `/tab` | List all associates sorted by debt |
| `/associate` | Select and manage an associate's debt |
| `/assets` | List all assets sorted by stock |
| `/asset` | Select and manage an asset's stock |

## Tech Stack

- [discord.py](https://github.com/Rapptz/discord.py) 2.7.1+ — Slash commands and UI components
- [TinyDB](https://github.com/msiemens/tinydb) — Lightweight JSON database
- [watchfiles](https://github.com/samuelcolvin/watchfiles) — Hot reload on file changes
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment variable management

## Setup

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- A Discord bot token

### Installation

```bash
git clone https://github.com/stafawashere/ledger-bot.git
cd ledger-bot
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
TOKEN=your_discord_bot_token
```

### Running

```bash
uv run bot.py
```

## Project Structure

```
ledger-bot/
├── bot.py
├── cogs/
│   ├── ledger/          # Balance management + history export
│   ├── tab/             # Associate & debt tracking
│   └── assets/          # Asset & stock management
├── utility/
│   ├── database.py      # TinyDB models (Tab, Assets, Balance, History, Ledger)
│   ├── embeds.py        # Discord embed helpers
│   ├── views.py         # Shared SelectView wrapper
│   └── __init__.py      # Utility functions (UUID, parsing, truncation)
├── ledger.json          # Database (auto-generated)
└── pyproject.toml
```

## License

MIT
