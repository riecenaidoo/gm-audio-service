import logging
import typing

import discord
from discord import Intents, Guild, VoiceChannel

import utils

_log = logging.getLogger(__name__)
_log.addHandler(utils.HANDLER)
_log.setLevel(logging.INFO)


class Channel:
    def __init__(self, channel: VoiceChannel):
        self.id: int = channel.id
        self.name: str = channel.name

    def serialize(self) -> dict:
        return {"id": self.id, "name": self.name}


class Server:
    def __init__(self, server: Guild):
        self.id: int = server.id
        self.name: str = server.name

    def serialize(self) -> dict:
        return {"id": self.id, "name": self.name}


class AudioClient(discord.Client):
    """Discord Client that manages the streaming of audio into voice channels."""

    def __init__(self, *, intents: Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)

    def get_servers(self) -> list[Server]:
        return [Server(guild) for guild in self.guilds]

    def get_channels(self, server_id: int) -> list[Channel]:
        for server in self.guilds:
            if server.id == server_id:
                return [Channel(channel) for channel in server.voice_channels]
        raise Exception(f"Server with id: '{server_id}' does not exist.")

    async def join_channel_in_server(self, channel_id: int, server_id: int) -> None:
        for server in self.guilds:
            if server.id == server_id:
                for channel in server.voice_channels:
                    if channel.id == channel_id:
                        await discord.VoiceChannel.connect(channel)
                        _log.info("Joined: %s > %s.", server.name, channel.name)
                        return
                raise Exception(f"Channel with id: '{channel_id}' does not exist.")
        raise Exception(f"Server with id: '{server_id}' does not exist.")
