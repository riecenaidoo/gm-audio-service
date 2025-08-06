
from models.exception import EmptyQueueError

class Playlist:
    def __init__(self):
        self.songs = []
        self.history = []
        self.current = None
        
        
    def get_current_playlist(self):
        return self.songs
    
    def get_current_song(self):
        if self.is_songs_empty():
            raise EmptyQueueError('No songs in queue to add songs use a /PUT Request to add songs')
        return self.songs[0]
    
    def get_next_song(self):
        if self.is_songlist_empty():
            raise EmptyQueueError('No songs in queue')
        
        if self.is_queue_empty():
            raise EmptyQueueError('There are no songs after the current song')
        
        return self.songs[1]
        
    def is_queue_empty(self):
        return len(self.songs) == 1
    
    def is_songlist_empty(self):
        return len(self.songs) < 1
    
    def set_songlist(self, songs: list[Song]):
        self.songs = songs
        
    def set_current_song(self, song: Song):
        self.songs.insert(0, song)
    
    def set_queue_next(self, newSongs: list[Song]):
        self.songs[1:] = newSongs
        
    def clear_queue(self):
        self.songs = self.songs[:1]