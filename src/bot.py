import logging
import typing

import discord
from discord import Intents, Guild

import utils

_log = logging.getLogger(__name__)
_log.addHandler(utils.HANDLER)
_log.setLevel(logging.INFO)


class Server:
    def __init__(self, server: Guild):
        self.id = server.id
        self.name = server.name

    def serialize(self) -> dict:
        return {"id": self.id, "name": self.name}


class AudioClient(discord.Client):
    """Discord Client that manages the streaming of audio into voice channels."""

    def __init__(self, *, intents: Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)

    def get_servers(self) -> list[Server]:
        return [Server(guild) for guild in self.guilds]
