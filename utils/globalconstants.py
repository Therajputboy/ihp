class Config:
    SECRET_KEY = 'secret'
    JWT_EXPIRY_HOURS = 4

class CustomException(Exception):
    def __init__(self, message):
        self.message = message

    def to_dict(self):
        return {
            "message": self.message
        }