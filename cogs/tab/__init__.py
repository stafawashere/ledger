from discord import app_commands
from discord.ext import commands
from utility.embeds import error, info
from utility.database import Tab
from .components import TabListView, AssociateSelect
from utility.views import SelectView


class TabCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tab", description="Tab Overview & Manage Associates")
    async def tab(self, interaction):
        associates = sorted(Tab.get_all(), key=lambda a: a["debt"], reverse=True)
        if associates:
            lines = [f"> {i}. **{a['name']}** — ${a['debt']} debt" for i, a in enumerate(associates, 1)]
            description = "\n".join(lines)
        else:
            description = "No associates yet."

        await interaction.response.send_message(
            embed=info(description, title="Tab Overview"),
            view=TabListView(),
            ephemeral=True,
        )

    @app_commands.command(name="associate", description="View & Manage Associate")
    async def associate(self, interaction):
        associates = Tab.get_all()
        if not associates:
            return await interaction.response.send_message(
                embed=error("No associates found."), ephemeral=True
            )

        await interaction.response.send_message(
            view=SelectView(AssociateSelect(associates)),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(TabCog(bot))