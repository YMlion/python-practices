"""use tornado to implement websocket"""
import json
import tornado.ioloop
import tornado.web
import tornado.websocket


class User():

    def __init__(self, token):
        self.token = token
        self._room_id = None

    @property
    def room_id(self):
        return self._room_id

    @room_id.setter
    def room_id(self, value):
        self._room_id = value


class MsgHandler(tornado.websocket.WebSocketHandler):   
    users = []

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print('recieved data from client is ' + message)
        dict_data = json.loads(message)
        action = dict_data['action']
        if action == 'exit':
            self.close()
        elif action == 'token':
            token = dict_data['data']
            print('the user token is ' + token)
            if not token or token == '':
                self.write_error(101)
                self.close()
            else:
                MsgHandler.users.append(User(token))
        elif action == 'start':
            game = dict_data['data']
            if game == 'draw_guess':
                result = {'code': 250, 'action': 'start', 'result': 55465}
                self.write_message(json.dumps(result))

    def on_close(self):
        print("WebSocket closed")


def main():
    app = tornado.web.Application([(r"/", MsgHandler), ])
    app.listen(8002, '10.32.8.172')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
