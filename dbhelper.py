import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False) #TODO CHECK THREAD = TRUE
        #TODO FIND A BETTER WAY WITH THREAD SAFETY

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS config (chat_id text PRIMARY KEY, username text, hour INT)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, item_text):
        stmt = "INSERT INTO items (description) VALUES (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_config(self, item_text):
        stmt = "DELETE FROM items WHERE description = (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_config(self, chat_id):
        stmt = "SELECT username, hour FROM config WHERE chat_id=?"
        cur = self.conn.execute(stmt, chat_id)

        if cur.rowcount > 0:
            row = self.conn.execute(stmt, chat_id).fetchone()
            return Config(chat_id, cur[0], cur[1])

        return None

    def set_config(self, chat_id, username = None, hour = None):
        try:
            chat_id = str(chat_id)
            print("Chat: " + chat_id)
            query = "SELECT username, hour FROM config WHERE chat_id=?"
            cur = self.conn.execute(query, (chat_id, ))
            row = None
            for x in cur:
                row = Config(chat_id, x[0], x[1])

            if row is not None:
                print("Exists")
                row.update(username, hour)
                stmt = "UPDATE config SET username=?, hour=? WHERE chat_id=?"
                self.conn.execute(stmt, (row.username, row.hour, row.chat_id, ))
                self.conn.commit()
                return row
            else:
                print("Not exists")
                stmt = "INSERT INTO config (chat_id, username, hour) VALUES (?, ?, ?)"
                self.conn.execute(stmt, (chat_id, username, hour, ))
                self.conn.commit()
                return Config(chat_id, username, hour)
        except Exception as e:
            print(e)

        return None

class Config:

    def __init__(self, chat_id="", username="", hour=0):
        self.chat_id = str(chat_id)
        self.username = username
        self.hour = hour

    def update(self, username, hour):
        if username is not None:
            self.username = username
        if hour is not None:
            self.hour = hour

    def to_string(self):
        return "chat: " + self.chat_id + " | Username: " + self.username\
                + " | Hour: " + str(self.hour) 
