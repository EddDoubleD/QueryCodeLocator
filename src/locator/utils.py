class EndOfMessage:
    def __init__(self, attempts: int):
        self.attempts = attempts

    def checkOver(self):
        return self.attempts > 0

    def decrement(self):
        self.attempts -= 1
