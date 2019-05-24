
class ChatConfig:

    def __init__(self, chat_id="", username="", hour=0, days=""):
        self.chat_id = str(chat_id)

        if username is None:
            self.username = "(not set)"
        else:
            self.username = username

        if hour is None:
            self.hour = "(not set)"
        else:
            self.hour = hour

        if days is None:
            self.days = "(not set)"
        else:
            self.days = days

    def update(self, username=None, hour=None, days=None):
        if username is not None:
            self.username = username
        if hour is not None:
            self.hour = hour
        if days is not None:
            self.days = days

    def to_string(self):
        msg = ""

        if not self.valid():
            msg += "\nYou must setup every field for the bot to work on this chat.\n\n"

        msg += "Username: @" + self.username

        msg += "Notification time: " + self.days + " at " + str(self.hour) + " o'clock."

        return msg

    def valid(self):
        return self.chat_id is not None and self.username is not None and self.days is not None and \
               self.hour is not None
