from typing import List
from models.requests import PathParam
from models.responses import Channel, ErrorResponse, Server
from quart_schema import validate_response, validate_request
import functools

class ServerController:
    def __init__(self, audio_client, api, playlist):
        self.audio_client = audio_client
        self.api = api
        self.playlist = playlist
        self.register_routes()
    
    async def check_connected_to_voice(func):
        pass
    
    def register_routes(self):
        
        @self.api.get('/')
        # @validate_response(Server)
        async def get_info():
            response = self.audio_client.serialize()
            return response
        
        @self.api.get('/servers')
        @validate_response(List[Server.Server])
        async def get_servers():
            response = self.audio_client.get_servers()
            return response
        
        @self.api.get('/servers/<int:id>/channels')
        async def get_channels(id: int):
            try:
                path = PathParam.PathParam(id=id)
            except TypeError as e:
                print(e)
                return ErrorResponse.ErrorResponse(error='Malformed param',status= 400)
            channels = self.audio_client.get_channels(path.id)
            return channels

        @self.api.get('/servers/<int:id>/playlist')
        async def get_playlist(id: int):
            pass