import sqlite3

def open_sqlite3():
    conn = sqlite3.connect('db/dg.db')
    cursor = conn.cursor()
    cursor.execute('create table user (token varchar(50) primary key, id varchar(50), name varchar(20), avatar varchar(100))')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456780", "0001", "张三", "http://img3.imgtn.bdimg.com/it/u=1121475478,2545730346&fm=214&gp=0.jpg")')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456781", "0002", "李四", "http://www.onegreen.net/QQ/UploadFiles/201301/2013010610135777.jpg")')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456782", "0003", "王五", "http://pic3.duowan.com/news/1005/138381138259/138381146937.jpg")')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456783", "0004", "六六", "http://img5.imgtn.bdimg.com/it/u=114395345,3231482796&fm=27&gp=0.jpg")')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456784", "0005", "七七", "http://pic.wenwen.soso.com/p/20150128/20150128123302-300234987.jpg")')
    cursor.execute('insert into user (token, id, name, avatar) values ("123456785", "0006", "胡巴", "http://diy.qqjay.com/u/files/2014/1208/b989d1dab21e4e283b86f23444db0f6e.jpg")')
    print('table row count is %s' %  cursor.rowcount)
    cursor.close()
    conn.commit()
    conn.close()

def fetch_user(token):
    conn = sqlite3.connect('db/dg.db')
    cursor = conn.cursor()
    cursor.execute('select * from user where token=?', (token,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    print(user)
    return user

if __name__ == "__main__":
    open_sqlite3()
