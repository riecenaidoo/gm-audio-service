import asyncio

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from bot import AudioClient, ServerAudio
from utils import to_thread


class AudioServiceAPI(Flask):
    def __init__(self, client: AudioClient, import_name: str):
        super().__init__(import_name)
        self.client = client
        self.cors = CORS(self, resources={r"/servers/*": {"origins": "http://localhost:4200"}})
        self._add_routes()

    @to_thread
    def start(self, host, port):
        """|coro|

        Wrapper function for starting the Flask API server async in a thread.
        """
        self.run(host=host, port=port)

    def _add_routes(self):
        self.add_url_rule("/servers", view_func=self._get_servers)
        self.add_url_rule(
            "/servers/<int:server_id>/channels", view_func=self._get_channels
        )
        self.add_url_rule(
            "/servers/<int:server_id>/audio",
            view_func=self._server_audio,
            methods=["GET", "POST", "DELETE"],
        )

    def _get_servers(self) -> Response:
        return jsonify([server.serialize() for server in self.client.get_servers()])

    def _get_channels(self, server_id: int) -> Response:
        return jsonify(
            [channel.serialize() for channel in self.client.get_channels(server_id)]
        )

    def _server_audio(self, server_id: int) -> Response:
        server_audio: ServerAudio = self.client.get_server_audio(server_id)

        match request.method:
            case "GET":
                if server_audio.is_connected():
                    return jsonify(server_audio.serialize())
                return jsonify(404)
            case "POST":
                data = request.get_json()
                channel_id: int = int(data.get("channel_id"))
                asyncio.run_coroutine_threadsafe(
                    server_audio.join_channel(channel_id), self.client.loop
                )
                return jsonify(200)
            case "DELETE":
                asyncio.run_coroutine_threadsafe(
                    server_audio.disconnect(), self.client.loop
                )
                return jsonify(200)
            case _:
                return jsonify(400)
