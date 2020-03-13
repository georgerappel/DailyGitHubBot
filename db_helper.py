import sqlite3
from chat_config import ChatConfig


class DBHelper:
    def __init__(self, dbpath="db_bot.sqlite"):
        self.dbname = dbpath
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
        # TODO Encontrar melhor solução para banco de dados (postgres local? mysql?). Ler abaixo:
        # O SQLite parece não ser Thread safe, o que pode causar problemas se dois comandos diferentes forem executados
        # ao mesmo tempo. A princípio, como cada tupla só é acessada pelo próprio chat, não deve haver inconsistências.
        # Outro problema é salvar os dados do SQLite, porque em alguns servidores (heroku), ao fazer o redeploy, ele
        # apaga o arquivo .sqlite e refaz o repositório, causando perda dos dados.

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS config (chat_id text PRIMARY KEY, username text, hour INT, days text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def get_config(self, chat_id):
        try:
            chat_id = str(chat_id)
            stmt = "SELECT username, hour, days FROM config WHERE chat_id=?"
            cur = self.conn.execute(stmt, (chat_id,))

            for x in cur:
                return ChatConfig(chat_id, x[0], x[1], x[2])
        except Exception as e:
            print(e)
        return None

    def set_config(self, chat_id, username=None, hour=None, days=None):
        chat_id = str(chat_id)

        query = "SELECT username, hour, days FROM config WHERE chat_id=?"
        cur = self.conn.execute(query, (chat_id, ))
        row = None

        for x in cur:
            row = ChatConfig(chat_id, username=x[0], hour=x[1], days=x[2])

        if row is not None:
            # Chat already on the database
            row = row.update(username, hour, days)  # Will update the fields that are not of NoneType
            stmt = "UPDATE config SET username=?, hour=?, days=? WHERE chat_id=?"
            self.conn.execute(stmt, (row.username, row.hour, row.days, row.chat_id, ))
            self.conn.commit()
        else:
            # Chat not on the database yet
            row =  ChatConfig(chat_id, username, hour, days)
            stmt = "INSERT INTO config (chat_id, username, hour, days) VALUES (?, ?, ?, ?)"
            self.conn.execute(stmt, (row.chat_id, row.username, row.hour, row.days, ))
            self.conn.commit()

        return row

    def all_configs(self):
        stmt = "SELECT chat_id, username, hour, days FROM config"
        cur = self.conn.execute(stmt)
        chats = []
        for row in cur:
            chats.append(ChatConfig(row[0], row[1], row[2], row[3]))

        return chats

    # def delete_config(self, item_text):
    #     stmt = "DELETE FROM items WHERE description = (?)"
    #     args = (item_text, )
    #     self.conn.execute(stmt, args)
    #     self.conn.commit()
