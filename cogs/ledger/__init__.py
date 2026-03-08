from discord import app_commands
from discord.ext import commands
from utility.embeds import info, success
from utility.database import History, Ledger, Tab, Assets, Balance
from .components import LedgerView, WipeConfirmView


class LedgerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ledger", description="Ledger Overview & Manage Balance")
    async def ledger(self, interaction):
        await interaction.response.send_message(
            embed=info(
                title="Ledger Overview",
                fields=[
                    {"name": "Balance / Predicted", "value": f"${Balance.get()} / ${Balance.predict()}", "inline": True},
                    {"name": "Associates", "value": str(Tab.count()), "inline": True},
                    {"name": "Assets", "value": str(Assets.count()), "inline": True},
                    {"name": "Recent History", "value": History.format(), "inline": False},
                ]
            ),
            view=LedgerView(),
        )

    @app_commands.command(name="wipe", description="Wipe Ledger")
    async def wipe_ledger(self, interaction):
        await interaction.response.send_message(
            embed=info("**Are you sure?** This is irreversible.", title="Wipe Ledger"),
            view=WipeConfirmView(),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(LedgerCog(bot))