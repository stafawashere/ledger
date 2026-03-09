import io
import discord
from utility.embeds import success, error, info
from utility import parse_float, generate_uuid
from utility.database import Assets, History
from utility.views import SelectView


class AddAssetModal(discord.ui.Modal, title="Assets Overview & Manage Stock"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Asset name",
        required=True,
    )
    unit = discord.ui.TextInput(
        label="Stock Unit",
        placeholder="tab, g, mg",
        required=True,
    )
    current_stock = discord.ui.TextInput(
        label="Current Stock",
        placeholder="Stock amount",
        required=False,
    )
    display_image = discord.ui.TextInput(
        label="Display Image",
        placeholder="Image Link/URL",
        required=False,
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        display_image = self.display_image.value or ""
        stock = parse_float(self.current_stock.value)
        if stock is None:
            return await interaction.response.send_message(
                embed=error("Invalid stock amount."), ephemeral=True
            )

        asset_id = generate_uuid()
        Assets.add_asset(self.name.value, asset_id, self.unit.value, display_image, stock)
        await interaction.response.send_message(
            embed=success(f"**{self.name.value} (`{asset_id}`)**{f' → {int(stock)} {self.unit.value}(s) in stock' if stock else ''}", thumbnail=display_image)
        )


class ManageAssetModal(discord.ui.Modal):
    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter amount",
        required=True,
    )
    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Reason for change",
        required=False,
    )

    def __init__(self, action, asset):
        super().__init__(title=f"{action.capitalize()} Stock — {asset['name']}"[:45])
        self.action = action
        self.asset = asset

    async def on_submit(self, interaction: discord.Interaction):
        amount = parse_float(self.amount.value)
        if amount is None:
            return await interaction.response.send_message(
                embed=error("Invalid amount."), ephemeral=True
            )

        new_stock, old_stock = Assets.update_stock(self.asset["id"], amount, self.reason.value, self.action)

        unit = self.asset["unit"]
        await interaction.response.send_message(embed=success(
            f"{self.asset['name']} stock is now {int(old_stock)} {unit}(s) → {int(new_stock)} {unit}(s)",
            title=f"Stock {self.action.capitalize()}",
        ))


class AssetActionButton(discord.ui.Button):
    def __init__(self, label, style, action, asset, row=0):
        super().__init__(label=label, style=style, row=row)
        self.action = action
        self.asset = asset

    async def callback(self, interaction: discord.Interaction):
        asset = Assets.find(self.asset["id"])
        await interaction.response.send_modal(ManageAssetModal(self.action, asset))


class AssetSettingsModal(discord.ui.Modal, title="Asset Settings"):
    def __init__(self, asset):
        super().__init__()
        self.asset = asset
        self.name_input = discord.ui.TextInput(
            label="Name",
            default=asset["name"],
            required=True,
        )
        self.unit_input = discord.ui.TextInput(
            label="Stock Unit",
            default=asset["unit"],
            required=True,
        )
        self.stock_input = discord.ui.TextInput(
            label="Current Stock",
            default=str(int(asset["stock"])),
            required=True,
        )
        self.image_input = discord.ui.TextInput(
            label="Thumbnail URL (256x256)",
            default=asset.get("display_image", ""),
            required=False,
        )
        self.add_item(self.name_input)
        self.add_item(self.unit_input)
        self.add_item(self.stock_input)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        stock = parse_float(self.stock_input.value)
        if stock is None:
            return await interaction.response.send_message(
                embed=error("Invalid stock amount."), ephemeral=True
            )

        Assets.update_settings(
            self.asset["id"],
            self.name_input.value,
            self.unit_input.value,
            self.image_input.value or "",
        )

        old_stock = self.asset["stock"]
        if stock != old_stock:
            Assets.update_stock(self.asset["id"], stock, "Set via settings", "set")

        await interaction.response.send_message(
            embed=success(f"Updated **{self.name_input.value}**"),
            ephemeral=True,
        )


class AssetSettingsButton(discord.ui.Button):
    def __init__(self, asset):
        super().__init__(label="Settings", style=discord.ButtonStyle.gray, row=1)
        self.asset = asset

    async def callback(self, interaction: discord.Interaction):
        asset = Assets.find(self.asset["id"])
        await interaction.response.send_modal(AssetSettingsModal(asset))


class ExportHistoryButton(discord.ui.Button):
    def __init__(self, asset):
        super().__init__(label="Export History", style=discord.ButtonStyle.gray, row=1)
        self.asset = asset

    async def callback(self, interaction: discord.Interaction):
        content = History.export(inclusion=["assets", self.asset["name"]])
        file = discord.File(io.BytesIO(content.encode()), filename=f"{self.asset['name']}_history.txt")
        await interaction.response.send_message(file=file, ephemeral=True)


class AssetOverviewView(discord.ui.View):
    def __init__(self, asset):
        super().__init__()
        self.add_item(AssetActionButton("Increase Stock", discord.ButtonStyle.green, "add", asset))
        self.add_item(AssetActionButton("Decrease Stock", discord.ButtonStyle.red, "remove", asset))
        self.add_item(AssetSettingsButton(asset))
        self.add_item(ExportHistoryButton(asset))


class AssetSelect(discord.ui.Select):
    def __init__(self, asset_list):
        options = [
            discord.SelectOption(
                label=a["name"],
                value=a["id"],
                description=f"ID: {a['id']} | Stock: {int(a['stock'])} {a['unit']}(s)"
            )
            for a in asset_list[:25]
        ]
        super().__init__(placeholder="Select an asset", options=options)

    async def callback(self, interaction: discord.Interaction):
        asset = Assets.find(self.values[0])
        await interaction.response.send_message(
            embed=info(
                title="Asset Overview",
                thumbnail=asset.get("display_image"),
                fields=[
                    {"name": "Name", "value": asset["name"], "inline": True},
                    {"name": "UUID", "value": asset["id"], "inline": True},
                    {"name": "Stock Unit", "value": asset["unit"], "inline": True},
                    {"name": "Stock", "value": f"{int(asset['stock'])} `{asset['unit']}(s)`", "inline": False}
                ]
            ),
            view=AssetOverviewView(asset),
            ephemeral=True,
        )


class DeleteAssetSelect(discord.ui.Select):
    def __init__(self, asset_list):
        options = [
            discord.SelectOption(
                label=a["name"],
                value=a["id"],
                description=f"ID: {a['id']} | Stock: {int(a['stock'])} {a['unit']}(s)",
            )
            for a in asset_list[:25]
        ]
        super().__init__(placeholder="Select an asset to delete", options=options)

    async def callback(self, interaction: discord.Interaction):
        asset = Assets.find(self.values[0])
        Assets.remove_asset(asset["id"])
        await interaction.response.send_message(
            embed=success(f"Deleted asset **{asset['name']}** (`{asset['id']}`)"),
            ephemeral=True,
        )


class AssetsListView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="New Asset", style=discord.ButtonStyle.green)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddAssetModal())

    @discord.ui.button(label="Delete Asset", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        asset_list = Assets.get_all()
        if not asset_list:
            return await interaction.response.send_message(
                embed=error("No assets to delete."), ephemeral=True
            )
        await interaction.response.send_message(
            view=SelectView(DeleteAssetSelect(asset_list)),
            ephemeral=True,
        )