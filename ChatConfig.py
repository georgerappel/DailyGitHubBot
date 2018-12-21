
class ChatConfig:

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
        msg = ""

        if not self.valid():
            msg += "You must configure all fields for the bot to work on this chat.\n"

        msg += "Username: "
        if self.username is not None:
            msg += "@" + self.username
        else:
            msg += "not set"
        msg += ".\n"

        msg += "Notification time: "
        if self.hour is not None:
            msg += str(self.hour) + " o'clock, daily"
        else:
            msg += "not set"
        msg += ".\n"

        return msg

    def valid(self):
        return self.chat_id is not None and\
               self.username is not None and\
               self.hour is not None
