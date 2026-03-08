from discord import app_commands
from discord.ext import commands
from utility.embeds import error, info
from utility.database import Assets, History
from .components import AssetsListView, AssetSelect
from utility.views import SelectView


class AssetsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="assets", description="Assets Overview & Manage Assets")
    async def assets(self, interaction):
        asset_list = sorted(Assets.get_all(), key=lambda a: a["stock"], reverse=True)
        if asset_list:
            lines = [f"> {i}. **{a['name']}** — `{int(a['stock'])}`{a['unit']}(s)" for i, a in enumerate(asset_list, 1)]
            description = "\n".join(lines)
        else:
            description = "No assets yet."

        await interaction.response.send_message(
            embed=info(
                description,
                title="Assets Overview",
                fields=[{
                    "name": "Recent History", "value": History.export(limit=7, format=True, compact=True, inclusion=["assets"]), "inline": False
                }]),
            view=AssetsListView()
        )

    @app_commands.command(name="asset", description="View & Manage Asset Stock")
    async def asset(self, interaction):
        asset_list = Assets.get_all()
        if not asset_list:
            return await interaction.response.send_message(
                embed=error("No assets found."), ephemeral=True
            )
        
        await interaction.response.send_message(
            view=SelectView(AssetSelect(asset_list)),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(AssetsCog(bot))