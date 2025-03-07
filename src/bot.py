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
        return {"id": str(self.id), "name": self.name}


class Server:
    def __init__(self, server: Guild):
        self.id: int = server.id
        self.name: str = server.name

    def serialize(self) -> dict:
        return {"id": str(self.id), "name": self.name}


class ServerAudio:
    def __init__(self, server: Guild):
        self._server: Guild = server

    def _get_channel(self, channel_id: int) -> VoiceChannel:
        for channel in self._server.voice_channels:
            if channel.id == channel_id:
                return channel
        raise Exception(
            f"Channel with id: '{channel_id}' does not exist in Server: '{self._server.name}'."
        )

    async def join_channel(self, channel_id: int):
        channel: VoiceChannel = self._get_channel(channel_id)
        await discord.VoiceChannel.connect(channel)
        _log.info("Joined: %s > %s.", self._server.name, channel.name)

    async def disconnect(self):
        if not self._server.voice_client:
            _log.warning(
                "Can't disconnect from %s - not connected to any channel",
                self._server.name,
            )
            return
        await self._server.voice_client.disconnect(force=True)
        _log.info("Disconnected from %s.", self._server.name)


class AudioClient(discord.Client):
    """Discord Client that manages the streaming of audio into voice channels."""

    def __init__(self, *, intents: Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)

    def get_servers(self) -> list[Server]:
        return [Server(guild) for guild in self.guilds]

    def _get_server(self, server_id: int) -> Guild:
        for server in self.guilds:
            if server.id == server_id:
                return server
        raise Exception(f"Server with id: '{server_id}' does not exist.")

    def get_channels(self, server_id: int) -> list[Channel]:
        server: Guild = self._get_server(server_id)
        return [Channel(channel) for channel in server.voice_channels]

    def get_server_audio(self, server_id: int) -> ServerAudio:
        return ServerAudio(self._get_server(server_id))
