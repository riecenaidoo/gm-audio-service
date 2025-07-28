

class Playlist:
    def __init__(self, client):
        self.client = client
        self.songs = {}
        self.history = {}