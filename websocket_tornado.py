"""use tornado to implement websocket"""
import tornado.ioloop
import tornado.web
import tornado.websocket
import json


class MsgHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print('recieved data from client is ' + message)
        # self.write_message(u"You said: " + message)
        dict_data = json.loads(message)
        action = dict_data['action']
        if action == 'exit':
            self.close()
        elif action == 'token':
            token = dict_data['data']
            print('the user token is ' + token)
            if token == None:
                self.write_error(101)
                self.close()
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
