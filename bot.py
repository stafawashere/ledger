import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from watchfiles import awatch
from utility.database import Ledger
from utility.embeds import set_icon


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def cog_watcher():
    async for changes in awatch("./cogs"):
        for ch, path in changes:
            if path.endswith(".py"):
                parts = os.path.normpath(path).split(os.sep)
                cogs_idx = parts.index("cogs")
                ext = f"cogs.{parts[cogs_idx + 1]}"
                try:
                    await bot.reload_extension(ext)
                    print(f"reloaded {ext}")
                except Exception as e:
                    print(f"failed to reload {ext}: {e}")


@bot.event
async def on_ready():
    Ledger.init()
    
    for name in os.listdir("./cogs"):
        path = os.path.join("./cogs", name)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "__init__.py")):
            await bot.load_extension(f"cogs.{name}")
            print(f"loaded {name}")
    await bot.tree.sync()
    bot.loop.create_task(cog_watcher())
    set_icon(bot.user.display_avatar.url)

    print(f"logged in as {bot.user}")


bot.run(os.getenv("DISCORD_TOKEN"))