import io
import discord
from utility.embeds import success, error, info
from utility import parse_float, generate_uuid
from utility.database import Tab, History
from utility.views import SelectView


class AddAssociateModal(discord.ui.Modal, title="Add Associate"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Associate name",
        required=True,
    )
    inital_debt = discord.ui.TextInput(
        label="Pre-Existing Debt",
        placeholder="Already in debt? $$",
        required=False,
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        debt = parse_float(self.inital_debt.value)
        if debt is None:
            return await interaction.response.send_message(
                embed=error("Invalid debt amount."), ephemeral=True
            )

        associate_id = generate_uuid()
        Tab.add_associate(self.name.value, associate_id, debt)
        await interaction.response.send_message(
            embed=success(f"New associate **{self.name.value} (`{associate_id}`)**{f' with ${debt} debt' if debt else ''}")
        )


class ManageDebtModal(discord.ui.Modal):
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

    def __init__(self, action, associate):
        super().__init__(title=f"{action.capitalize()} Debt — {associate['name']}")
        self.action = action
        self.associate = associate

    async def on_submit(self, interaction: discord.Interaction):
        amount = parse_float(self.amount.value)
        if amount is None:
            return await interaction.response.send_message(
                embed=error("Invalid amount."), ephemeral=True
            )

        new_debt, old_debt = Tab.update_debt(self.associate["id"], amount, self.reason.value, self.action)
        await interaction.response.send_message(embed=success(
            f"{self.associate['name']} now owes a total of ${old_debt} → ${new_debt}",
            title=f"Debt {self.action.capitalize()}",
        ))


class DebtActionButton(discord.ui.Button):
    def __init__(self, label, style, action, associate):
        super().__init__(label=label, style=style)
        self.action = action
        self.associate = associate

    async def callback(self, interaction: discord.Interaction):
        associate = Tab.find(self.associate["id"])
        await interaction.response.send_modal(ManageDebtModal(self.action, associate))


class ExportHistoryButton(discord.ui.Button):
    def __init__(self, associate):
        super().__init__(label="Export History", style=discord.ButtonStyle.gray)
        self.associate = associate

    async def callback(self, interaction: discord.Interaction):
        content = History.export(inclusion=["tab", self.associate["name"]])
        file = discord.File(io.BytesIO(content.encode()), filename=f"{self.associate['name']}_history.txt")
        await interaction.response.send_message(file=file, ephemeral=True)


class AssociateOverviewView(discord.ui.View):
    def __init__(self, associate):
        super().__init__()
        self.add_item(DebtActionButton("Increase Debt", discord.ButtonStyle.green, "add", associate))
        self.add_item(DebtActionButton("Decrease Debt", discord.ButtonStyle.red, "remove", associate))
        self.add_item(DebtActionButton("Set Debt", discord.ButtonStyle.blurple, "set", associate))
        self.add_item(ExportHistoryButton(associate))


class AssociateSelect(discord.ui.Select):
    def __init__(self, associates):
        options = [
            discord.SelectOption(
                label=a["name"],
                value=a["id"],
                description=f"ID: {a['id']} | Owes: ${a['debt']}",
            )
            for a in associates[:25]
        ]
        super().__init__(placeholder="Select an associate", options=options)

    async def callback(self, interaction: discord.Interaction):
        associate = Tab.find(self.values[0])
        await interaction.response.send_message(
            embed=info(
                title="Associate Overview",
                fields=[
                    {"name": "Name", "value": associate["name"], "inline": True},
                    {"name": "Uuid", "value": associate["id"], "inline": True},
                    {"name": "Debt", "value": f"**${associate['debt']}**", "inline": True},
                    {"name": "Recent History", "value": History.export(limit=7, format=True, compact=True, inclusion=["tab", associate["name"]]), "inline": False}
                ]
            ),
            view=AssociateOverviewView(associate),
            ephemeral=True
        )


class DeleteAssociateSelect(discord.ui.Select):
    def __init__(self, associates):
        options = [
            discord.SelectOption(
                label=a["name"],
                value=a["id"],
                description=f"ID: {a['id']} | Owes: ${a['debt']}",
            )
            for a in associates[:25]
        ]
        super().__init__(placeholder="Select an associate to delete", options=options)

    async def callback(self, interaction: discord.Interaction):
        associate = Tab.find(self.values[0])
        Tab.remove_associate(associate["id"])
        await interaction.response.send_message(
            embed=success(f"Deleted associate **{associate['name']}** (`{associate['id']}`)"),
            ephemeral=True,
        )


class TabListView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="New", style=discord.ButtonStyle.green)
    async def new_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddAssociateModal())

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        associates = Tab.get_all()
        if not associates:
            return await interaction.response.send_message(
                embed=error("No associates to delete."), ephemeral=True
            )
        
        await interaction.response.send_message(
            view=SelectView(DeleteAssociateSelect(associates)),
            ephemeral=True,
        )