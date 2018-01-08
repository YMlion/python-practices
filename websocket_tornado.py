import tornado.ioloop
import tornado.web
import tornado.websocket


class MsgHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        print('recieve data from client : %s' % message)


def main():
    settings = {
        'template_path': 'templates',
        'static_path': 'static',
    }
    app = tornado.web.Application([(r"/", MsgHandler), ], settings)
    app.listen(9999)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
