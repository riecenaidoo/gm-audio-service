from typing import List
from models.exception import EmptyQueueError
from models.requests import PathParam, Song
from models.responses import Channel,Server, ErrorResponse

from quart_schema import validate_response, validate_request
import functools

class ServerController:
    def __init__(self, audio_client, api, playlist):
        self.audio_client = audio_client
        self.api = api
        self.register_routes()
    
    async def check_connected_to_voice(func):
        pass
    
    def register_routes(self):
        playlist = self.api.get_playlist()
        @self.api.get('/')
        async def get_info():
            response = self.audio_client.serialize()
            return response
        
        @self.api.get('/servers')
        @validate_response(List[Server])
        async def get_servers():
            response = self.audio_client.get_servers()
            return response
        
        @self.api.get('/servers/<int:id>/voice-channels')
        @validate_response(List[Channel], ErrorResponse)
        async def get_channels(id: int):
            try:
                path = PathParam.PathParam(id=id)
            except AttributeError:
                return ErrorResponse(error='Malformed param',status= 400)
            channels = self.audio_client.get_channels(path.id)
            return channels

        @self.api.get('/servers/<int:id>/playlist')
        @validate_response(list[Song], ErrorResponse)
        async def get_playlist(id: int) -> list[Song]:
            server = self.api._get_server()
            if server.connected_to().id != id:
                return ErrorResponse(error="", status=400)
            return playlist.get_current_playlist()
        
        @self.api.put('/servers/<int:id>/playlist')
        @validate_request(list[Song], ErrorResponse)
        async def replace_playlist(id: int, songs: list[Song]):
            try:
                playlist.set_songlist(songs)
            except:
                return ErrorResponse(error="Internal Server Error", status=500)
            return playlist.get_current_playlist()
        
        @self.api.patch('/servers/<int:id>/playlist')
        async def update_playlist(id: int):
            return [] #not 100% sure what this should do
        
        @self.api.delete('/servers/<int: id>/playlist')
        async def clear_playlist(id: int):
            playlist.clear_songlist()
            return playlist.get_current_playlist()
        
        @self.api.put('/servers/<int: id>/playlist/current')
        async def play_current_playlist(id: int, songs: list[Song]):
            playlist.set_songlist(songs)
            return playlist.get_current_playlist()
        
        @self.api.delete('/servers/<int: id>/playlist/current')
        async def skip_song(id: int):
            try:
                playlist.skip_song()
            except EmptyQueueError:
                return ErrorResponse(error="No more songs in queue", status=400)
            return playlist.get_current_playlist()
        
        @self.api.put('/servers/<int: id>/playlist/next')
        async def edit_queue(id: int, songs: list[Song]):
            playlist.set_queue_next(songs)
            return playlist.get_current_playlist()
        
        @self.api.delete('/servers/<int: id>/playlist/next')
        async def clear_queue(id: int):
            playlist.clear_songlist()
            return playlist.get_current_playlist()