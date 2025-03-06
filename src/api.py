import asyncio

from flask import Flask, Response, jsonify, request

from bot import AudioClient
from utils import to_thread


class AudioServiceAPI(Flask):
    def __init__(self, client: AudioClient, import_name: str):
        super().__init__(import_name)
        self.client = client
        self._add_routes()

    @to_thread
    def start(self, host, port):
        """|coro|

        Wrapper function for starting the Flask API server async in a thread.
        """
        self.run(host=host, port=port)

    def _add_routes(self):
        self.add_url_rule("/servers", view_func=self._get_servers)
        self.add_url_rule("/servers/<int:server_id>/channels", view_func=self._get_channels)
        self.add_url_rule("/servers/<int:server_id>/audio", view_func=self._create_audio_service, methods=['POST'])

    def _get_servers(self) -> Response:
        return jsonify([server.serialize() for server in self.client.get_servers()])

    def _get_channels(self, server_id:int) -> Response:
        return jsonify([channel.serialize() for channel in self.client.get_channels(server_id)])

    def _create_audio_service(self, server_id: int) -> Response:
        data = request.get_json()
        channel_id:int = int(data.get("channel_id"))
        for channel in self.client.get_channels(server_id):
            if channel.id == channel_id:
                asyncio.run_coroutine_threadsafe(self.client.join_channel_in_server(channel_id, server_id), self.client.loop)
                return jsonify(200)
        return jsonify(404)