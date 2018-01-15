"""
all model class
"""


class User():
    """用户bean"""

    def __init__(self, token, id_num, name, avatar):
        self.token = token
        self.id_num = id_num
        self.name = name
        self.avatar = avatar
        self._room_id = None
        self._game_playing = None
        self._game_ready = False

    @property
    def room_id(self):
        return self._room_id

    @room_id.setter
    def room_id(self, value):
        self._room_id = value

    @property
    def game_playing(self):
        return self._game_playing

    @game_playing.setter
    def game_playing(self, value):
        self._game_playing = value

    @property
    def game_ready(self):
        return self._game_ready

    @game_ready.setter
    def game_ready(self, value):
        self._game_ready = value

    def get_json_text(self):
        return {'id': self.id_num, 'name': self.name, 'avatar': self.avatar, 'state': self._game_ready}
