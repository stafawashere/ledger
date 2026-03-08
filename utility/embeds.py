import discord
from datetime import datetime


class Colors:
    SUCCESS = 0xaae6ba
    ERROR = 0xe38f8f
    WARNING = 0xcee075
    INFO = 0xb5b5b5
    PRIMARY = 0x5865F2

    
_icon_url = None
def set_icon(url):
    global _icon_url
    _icon_url = url


def embed(
    title="",
    description="",
    color=Colors.PRIMARY,
    fields=None,
    footer="Ledger",
    thumbnail=None,
    image=None,
    author=None,
):
    e = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(),
    )

    if fields:
        for field in fields:
            e.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", True),
            )

    if footer:
        e.set_footer(text=footer, icon_url=_icon_url)
    if thumbnail:
        e.set_thumbnail(url=thumbnail)
    if image:
        e.set_image(url=image)
    if author:
        e.set_author(name=author.get("name"), icon_url=author.get("icon"))

    return e


def success(description="", title="Success", **kwargs):
    return embed(title=title, description=description, color=Colors.SUCCESS, **kwargs)


def error(description="", title="Error", **kwargs):
    return embed(title=title, description=description, color=Colors.ERROR, **kwargs)


def warning(description="", title="Warning", **kwargs):
    return embed(title=title, description=description, color=Colors.WARNING, **kwargs)


def info(description="", title="Info", **kwargs):
    return embed(title=title, description=description, color=Colors.INFO, **kwargs)