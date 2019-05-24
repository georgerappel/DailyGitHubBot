import sqlite3
from ChatConfig import ChatConfig


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        # TODO CHECK THREAD = TRUE
        # TODO FIND A BETTER WAY WITH THREAD SAFETY

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS config (chat_id text PRIMARY KEY, username text, hour INT)"
        self.conn.execute(stmt)
        self.conn.commit()

    def get_config(self, chat_id):
        try:
            chat_id = str(chat_id)
            stmt = "SELECT username, hour FROM config WHERE chat_id=?"
            cur = self.conn.execute(stmt, (chat_id,))

            for x in cur:
                return ChatConfig(chat_id, x[0], x[1])
        except Exception as e:
            print(e)
        return None

    def set_config(self, chat_id, username=None, hour=None):
        chat_id = str(chat_id)

        query = "SELECT username, hour FROM config WHERE chat_id=?"
        cur = self.conn.execute(query, (chat_id, ))
        row = None

        for x in cur:
            row = ChatConfig(chat_id, x[0], x[1])

        if row is not None:
            # Chat already on the database
            row.update(username, hour)
            stmt = "UPDATE config SET username=?, hour=? WHERE chat_id=?"
            self.conn.execute(stmt, (row.username, row.hour, row.chat_id, ))
            self.conn.commit()
            return row
        else:
            # Chat not on the database yet
            stmt = "INSERT INTO config (chat_id, username, hour) VALUES (?, ?, ?)"
            self.conn.execute(stmt, (chat_id, username, hour, ))
            self.conn.commit()
            return ChatConfig(chat_id, username, hour)

    def all_configs(self):
        stmt = "SELECT chat_id, username, hour FROM config"
        cur = self.conn.execute(stmt)
        chats = []
        for row in cur:
            chats.append(ChatConfig(row[0], row[1], row[2]))

        return chats

    # def delete_config(self, item_text):
    #     stmt = "DELETE FROM items WHERE description = (?)"
    #     args = (item_text, )
    #     self.conn.execute(stmt, args)
    #     self.conn.commit()
