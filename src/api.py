from flask import Flask, Response, jsonify

from bot import AudioClient
from utils import to_thread


class AudioServiceAPI(Flask):
    def __init__(self, client: AudioClient, import_name: str):
        super().__init__(import_name)
        self.client = client

    @to_thread
    def start(self, host, port):
        """|coro|

        Wrapper function for starting the Flask API server async in a thread.
        """
        self.run(host=host, port=port)

