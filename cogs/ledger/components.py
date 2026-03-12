import io
import discord
from utility.embeds import success, error, warning
from utility import parse_float
from utility.database import Balance, History, Ledger


class BalanceModal(discord.ui.Modal):
    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter amount",
        required=True,
    )
    note = discord.ui.TextInput(
        label="Note",
        placeholder="Reason for change",
        required=False,
    )

    def __init__(self, action):
        super().__init__(title=f"{action.capitalize()} Balance")
        self.action = action

    async def on_submit(self, interaction: discord.Interaction):
        value = parse_float(self.amount.value, allow_negative=False)
        if value is None:
            return await interaction.response.send_message(
                embed=error("Invalid amount."), ephemeral=True
            )

        new_bal, old_bal = Balance.update(value, self.note.value, self.action)

        await interaction.response.send_message(embed=success(
            f"${old_bal} → ${new_bal}",
            title=f"Balance {self.action.capitalize()}",
        ))


class BalanceActionButton(discord.ui.Button):
    def __init__(self, label, style, action):
        super().__init__(label=label, style=style)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BalanceModal(self.action))


class LedgerView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(BalanceActionButton("Increase Bal", discord.ButtonStyle.green, "add"))
        self.add_item(BalanceActionButton("Decrease Bal", discord.ButtonStyle.red, "remove"))
        self.add_item(BalanceActionButton("Set Bal", discord.ButtonStyle.blurple, "set"))
        self.add_item(ExportHistoryActionButton("Export History", discord.ButtonStyle.gray, "export_history"))


class ExportHistoryActionButton(discord.ui.Button):
    def __init__(self, label, style, action):
        super().__init__(label=label, style=style)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        content = History.export()
        file = discord.File(io.BytesIO(content.encode()), filename="history.txt")
        await interaction.response.send_message(file=file, ephemeral=True)


class WipeConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Confirm Wipe", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        Ledger.wipe()
        await interaction.response.send_message(embed=success("Wiped entire Ledger"))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=warning("Wipe cancelled."), ephemeral=True
        )