import asyncio
from json import dumps

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from bot import AudioClient, ServerAudio
from utils import to_thread


class AudioServiceAPI(Flask):
    def __init__(self, client: AudioClient, import_name: str):
        super().__init__(import_name)
        self.client = client
        self.cors = CORS(
            self, resources={r"/servers/*": {"origins": "http://localhost:4200"}}
        )
        self._add_routes()

    @to_thread
    def start(self, host, port):
        """|coro|

        Wrapper function for starting the Flask API server async in a thread.
        """
        self.run(host=host, port=port)

    def _add_routes(self) -> None:
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
        """Supports GET, POST, DELETE"""
        server_audio: ServerAudio = self.client.get_server_audio(server_id)

        match request.method:
            case "GET":
                if server_audio.is_connected():
                    return jsonify(server_audio.serialize())
                body: dict = {
                    "error": "Server does not have an Audio client connected.",
                    "message": "An Audio client can be connected via a POST/ to this endpoint.",
                }
                return Response(
                    response=dumps(body), status=404, mimetype="application/json"
                )
            case "POST":
                data: dict = request.get_json()
                if "channel_id" not in data.keys():
                    body: dict = {
                        "error": "Required field 'channel_id' missing.",
                        "message": "You must specify the Channel in the Server to connect the Audio client to.",
                    }
                    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422
                    return Response(
                        response=dumps(body), status=422, mimetype="application/json"
                    )
                # Could validate this as well, and if not correct return 400.
                channel_id: int = int(data.get("channel_id"))
                # Should amend signature to grab the channel, and if not found return 400.
                asyncio.run_coroutine_threadsafe(
                    server_audio.join_channel(channel_id), self.client.loop
                )
                return Response(status=202)
            case "DELETE":
                if not server_audio.is_connected():
                    return Response(status=404)
                asyncio.run_coroutine_threadsafe(
                    server_audio.disconnect(), self.client.loop
                )
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202
                return Response(status=202)
            case _:
                raise Exception(f"Procedure for {request.method} is unmapped.")
