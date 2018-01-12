"""use tornado to implement websocket"""
import json
import tornado.ioloop
import tornado.web
import tornado.websocket
from dg_model import User
import sqlite_connec


class MsgHandler(tornado.websocket.WebSocketHandler):
    """cs消息交互处理"""
    users = set()

    def __init__(self, application, request, **kwargs):
        super(MsgHandler, self).__init__(application, request, **kwargs)
        self.user = None

    def open(self):
        MsgHandler.users.add(self)
        print(self)
        print("WebSocket opened")

    @staticmethod
    def notify_users(others, msg):
        """推送消息给用户"""
        for handler in others:
            handler.write_message(msg)

    def get_others(self):
        """获取当前房间其他用户"""
        # filter方法或者列表推导式，filter稍微复杂点
        return [h for h in MsgHandler.users if h.user is not None and h.user != self.user and h.user.room_id == self.user.room_id]

    def on_message(self, message):
        print('recieved data from client is ' + message)
        dict_data = json.loads(message)
        action = dict_data['action']
        if action == 'exit':
            self.close()
        elif action == 'token':  # token验证
            token = dict_data['data']
            print('the user token is ' + token)
            if not token or token == '':
                self.write_error(101)
                self.close()
            else:
                self.user = User(token)
                notify_msg = {'code': 250, 'action': 'user_info',
                              'result': {}}
                fetch_result = sqlite_connec.fetch_user(token)
                notify_msg['result']['token'] = fetch_result[0]
                notify_msg['result']['id'] = fetch_result[1]
                notify_msg['result']['name'] = fetch_result[2]
                notify_msg['result']['avatar'] = fetch_result[3]
                self.write_message(json.dumps(notify_msg))
        elif action == 'start':  # 开始游戏
            game = dict_data['data']
            if game == 'draw_guess':
                result = {'code': 250, 'action': 'start', 'result': 55465}
                self.user.room_id = result['result']
                self.write_message(json.dumps(result))
                # 通知其他人有人加入游戏
                others = self.get_others()
                notify_msg = {'code': 250, 'action': 'user_in',
                              'result': self.user.token}
                MsgHandler.notify_users(others, json.dumps(notify_msg))
        elif action == 'ready': # 准备
            game = dict_data['data']
            if game == 'draw_guess':
                self.user.game_ready = True
                others = self.get_others()
                notify_msg = {'code': 250, 'action': 'user_ready', 'result': self.user.token}
                MsgHandler.notify_users(others, json.dumps(notify_msg))
        elif action == 'quit_game':  # 退出游戏
            others = self.get_others()
            notify_msg = {'code': 250, 'action': 'user_quit',
                          'result': self.user.token}
            MsgHandler.notify_users(others, json.dumps(notify_msg))
            self.user = None

    def on_close(self):
        MsgHandler.users.remove(self)
        print("WebSocket closed")


def main():
    """main方法"""
    app = tornado.web.Application([(r"/", MsgHandler), ])
    app.listen(8002, '10.32.8.172')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
