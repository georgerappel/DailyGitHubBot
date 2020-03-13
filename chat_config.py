from datetime import datetime

valid_days = ["weekdays", "daily"]
DEFAULT_NOT_SET_STR = "(not set)"


class ChatConfig:

    def __init__(self, chat_id="", username="", hour=0, days="weekdays"):
        self.chat_id = str(chat_id)

        if username is None:
            self.username = DEFAULT_NOT_SET_STR
        else:
            self.username = username

        if hour is None:
            self.hour = DEFAULT_NOT_SET_STR
        else:
            self.hour = hour

        if days is not None and valid_days.__contains__(days):
            self.days = days
        else:
            self.days = "weekdays"  # Default to Weekdays

    def update(self, username=None, hour=None, days=None):
        if username is not None:
            self.username = username
        if hour is not None and 24 > hour >= 0:
            self.hour = hour
        if days is not None and valid_days.__contains__(days):
            self.days = days
        return self

    def to_string(self):
        msg = ""

        if not self.valid():
            msg += "\nYou must setup every field for the bot to work on this chat.\n\n"

        msg += "Username: @" + self.username + "\n"
        msg += "Notification time: " + self.days + " at " + str(self.hour) + " o'clock."
        return msg

    def should_send_message(self):
        if self.valid() \
                and self.hour == datetime.utcnow().hour \
                and ((self.days == "weekdays" and datetime.utcnow().weekday() < 5) or
                     self.days == "daily"):
            return True
        return False

    def valid(self):
        return self.chat_id is not None and self.chat_id is not "" \
               and self.username is not None and self.username is not DEFAULT_NOT_SET_STR and self.username is not "" \
               and self.days is not None and self.days in valid_days \
               and self.hour is not None and 0 <= self.hour < 24
