
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
        return "Username: @" + self.username + "\n" + "Notification hour: " + str(self.hour) + "\n" + "Days: " \
               + self.days
