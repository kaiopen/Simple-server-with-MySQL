import socketserver
import pymysql

users = {}


class Database:
    def __init__(self, host, user, password, database):
        try:
            self.conn = pymysql.connect(host, user, password, database)
            self.cursor = self.conn.cursor
        except:
            print("Error: connect mysql error")

    def self_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.fetchall()
        except:
            return -1


class Server(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.database = Database("localhost", "root", "ONE..py1*5", "shaking")
        print("[" + self.client_address[0] + "] " + "Connect database successfully.")

        try:
            self.handle()
        finally:
            print("[" + self.client_address[0] + "] " + "End service.")

    def handle(self):
        while True:
            receive = str(self.request.recv(1024), encoding="utf8").split('|')
            print(receive)
            if receive[0] == "11":
                self.login(receive)
            elif receive[0] == "01":
                self.game_result(receive)
            elif receive[0] == "000":
                self.top()
            elif receive[0] == "001":
                self.register(receive)
            else:
                break

    def login(self, receive):
        print("[" + self.client_address[0] + "] " + "Ask to login.")
        # receive = str(self.request.recv(1024), encoding="utf-8").split('|', 1)
        # print(receive)
        sql = "select strcmp('" + receive[2] + "', (select passwd from users where username ='" + receive[1] + "'));"
        if 0 == self.database.self_sql(sql)[0][0]:
            global users
            users[self.client_address[0]] = receive[1]
            print(users)
            self.request.sendall(bytes("1\n", encoding="utf8"))
            print("[" + self.client_address[0] + "] " + "Login successfully.")
        else:
            self.request.sendall(bytes("0\n", encoding="utf8"))
            print("[" + self.client_address[0] + "] " + "Fail to login.")

    def game_result(self, receive):
        print("[" + self.client_address[0] + "] " + "Game Result.")
        # receive = str(self.request.recv(1024), encoding="utf8")
        # print("[" + self.client_address[0] + "] " + "Score:" + receive[1])
        sql = "select score from users where username = '" + users[self.client_address[0]] + "';"
        if int(receive[1]) > self.database.self_sql(sql)[0][0]:
            sql = "update users set score = " + receive[1] + " where username = '" + users[self.client_address[0]] + "';"
            self.database.self_sql(sql)

    def top(self):
        print("[" + self.client_address[0] + "] " + "Ask for the Top.")
        sql = "select username, score from users order by score desc;"
        sends = self.database.self_sql(sql)
        for send in sends:
            print(send)
            self.request.sendall(bytes(send[0] + '|' + str(send[1]) + '\n', encoding="utf8"))
        self.request.sendall(bytes('0\n', encoding="utf8"))

    def register(self, receive):
        print("[" + self.client_address[0] + "] " + "Ask to register.")
        # receive = str(self.request.recv(1024), encoding="utf8").split('|', 1)
        # print(receive)
        sql = "select username from users where username ='" + receive[1] + "';"
        if not self.database.self_sql(sql):
            sql = "insert into users(username, passwd) values('" + receive[1] + "', '" + receive[2] + "');"
            self.database.self_sql(sql)
            print("[" + self.client_address[0] + "] " + "Register successfully.")
            self.request.sendall(bytes("1\n", encoding="utf8"))
        else:
            print("[" + self.client_address[0] + "] "
                  + ' Fail to register: The name has already existed.')
            self.request.sendall(bytes("0\n", encoding="utf8"))


if __name__ == '__main__':
    socketserver.ThreadingTCPServer(("192.168.43.102", 9999), Server).serve_forever()
