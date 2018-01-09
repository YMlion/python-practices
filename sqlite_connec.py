import sqlite3

def open_sqlite3():
    conn = sqlite3.connect('db/dg.db')
    cursor = conn.cursor()
    cursor.execute('create table user (token varchar(50) primary key, name varchar(20))')
    cursor.execute('insert into user (token, name) values ("123456789", "张三")')
    print('table row count is %s' %  cursor.rowcount)
    cursor.close()
    conn.commit()
    conn.close()

if __name__ == "__main__":
    open_sqlite3()
