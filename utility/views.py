import discord


class SelectView(discord.ui.View):
    def __init__(self, select):
        super().__init__()
        self.add_item(select)