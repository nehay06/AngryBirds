import constants.Constants as constants

class Message:

    msgID = 0

    def __init__(self, msgType, callerID, params):
        self.msgType = msgType
        self.msgID = self.getMessageID()
        self.callerID = callerID
        self.params = params

    def setParams(self, params):
        self.params = params

    @classmethod
    def getMessageID(cls):
        cls.msgID += 1
        return cls.msgID


    # The params are as follows:
    # 1) BIRD_APPROACHING: [hopcount, target_hit, duration]
    # 2)