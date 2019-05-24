
class ChatConfig:

    def __init__(self, chat_id="", username="", hour=0):
        self.chat_id = str(chat_id)

        if username is None:
            self.username = "(not set)"
        else:
            self.username = username

        if hour is None:
            self.hour = "(not set)"
        else:
            self.hour = hour

    def update(self, username, hour):
        if username is not None:
            self.username = username
        if hour is not None:
            self.hour = hour

    def to_string(self):
        return "Username: @" + self.username + "\n" + "Notification hour: " + str(self.hour)
