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

    def write_error(self, code, action):
        error_msg = {'code': code, 'action': action,
                     'data': 'error'}
        self.write_message(json.dumps(error_msg))

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
                self.write_error(101, 'token')
                # self.close()
            else:
                fetch_result = sqlite_connec.fetch_user(token)
                if fetch_result is None:
                    self.write_error(102, 'token')
                    return
                notify_msg = {'code': 250, 'action': 'user_info',
                              'data': {}}
                notify_msg['data']['token'] = fetch_result[0]
                notify_msg['data']['id'] = fetch_result[1]
                notify_msg['data']['name'] = fetch_result[2]
                notify_msg['data']['avatar'] = fetch_result[3]
                self.write_message(json.dumps(notify_msg))
                self.user = User(
                    token, fetch_result[1], fetch_result[2], fetch_result[3])
        elif action == 'start':  # 开始游戏
            game = dict_data['data']
            if game == 'draw_guess':
                # 返回room相关信息和玩家列表
                result = {'code': 250, 'action': 'start_room', 'data': {}}
                # 房间信息
                room_info = {'id': 6666, 'game': 'draw_guess'}
                room_users = []
                for room_user in MsgHandler.users:
                    if room_user.user is not None and room_user.user.room_id == room_info['id']:
                        room_users.append(room_user.user.get_json_text())
                result['data']['room'] = room_info
                result['data']['players'] = room_users
                self.user.room_id = room_info['id']
                self.write_message(json.dumps(result))
                # 通知其他人有人加入游戏
                others = self.get_others()
                notify_msg = {'code': 250, 'action': 'user_in',
                              'data': self.user.get_json_text()}
                MsgHandler.notify_users(others, json.dumps(notify_msg))
        elif action == 'ready':  # 准备
            game = dict_data['data']
            if game == 'draw_guess':
                self.user.game_ready = True
                others = self.get_others()
                notify_msg = {'code': 250, 'action': 'user_ready',
                              'data': self.user.id_num}
                MsgHandler.notify_users(others, json.dumps(notify_msg))
        elif action == 'quit_game':  # 退出游戏
            others = self.get_others()
            notify_msg = {'code': 250, 'action': 'user_quit',
                          'data': self.user.id_num}
            MsgHandler.notify_users(others, json.dumps(notify_msg))
            self.user = None

        elif action == 'msg_text':
            others = self.get_others()
            notify_msg = {'code': 250, 'action': 'notify_msg_text',
                          'data': dict_data['data']}
            MsgHandler.notify_users(others, json.dumps(notify_msg))

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
