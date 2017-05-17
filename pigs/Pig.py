import topology.NetworkMap as networkMap
import constants.Constants as constants
import Pyro4
from message.Message import Message



@Pyro4.expose
class Pig:
    msgID = 1
    # game over
    def __init__(self, ip, daemon, nameServer):
        """
        self.ip = pig's ip
        self.messageCache = initial message chache
        self.status = The pig's initial status
        self.alertCaller = the IP that alerted you
        self.orginalSender = Flag if this pig was the original sender of TAKE_SHELTER
        :param ip: Integer
        :param daemon: daemon to register
        :param nameServer: nameserver to register
        """
        self.ip = ip
        self.messageCache = []
        self._registerOnServer(daemon, nameServer)
        self.status = constants.PigConstants.PIG_ALIVE
        self.alertCaller = -1
        self.orginalSender = False

    def pushMessage(self, message):
        # check if game not over
        if message[1] not in self.messageCache:
            self.messageCache.append(message[1])
            if (message[0] == constants.MessageConstants.MSGTYPE_BIRD_APPROACHING):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleBirdApproachingMessage(message)
            elif (self.status == constants.PigConstants.PIG_ALIVE and message[0] == constants.MessageConstants.MSGTYPE_TAKE_SHELTER):
                # this is to ensure that if pig has been DEAD, it does not pass this
                # message on to other pigs
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleTakeShelterMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_STATUS):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleStatusMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                print "Acknowledgement receiver: {}".format(message[4])
                self.handleAcknowledgement(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_I_AM_SAFE):
                print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip,
                                                                                         message[2], message[1])
                self.handleIAmSafe(message)

    def handleIAmSafe(self, message):
        ownPhysicalAddress = self._getPhysicalAddress()
        if (message[3] == ownPhysicalAddress):
            # If you were the intended receiver
            self.status = constants.PigConstants.PIG_EVADED
        else:
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendIAmSafe(nbr, message)

    def sendIAmSafe(self, nbr, message):
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def handleBirdApproachingMessage(self, message):
        hopcount = message[3]
        targetHit = message[4]
        duration = message[5]

        if (self._isGettingAffected(targetHit)):
            self._sendAlert()

        else:
            self.nbrs = self._getNetworkNeighbours()
            hopcount = hopcount - 1
            for nbr in self.nbrs:
                self.sendBirdApproachingMessage(nbr, message)

    def sendBirdApproachingMessage(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        message[2] = self.ip
        pigProxy.pushMessage(message)

    def handleTakeShelterMessage(self, message):
        shelterAddress = message[3]
        ownPhysicalAddress = self._getPhysicalAddress()
        if (shelterAddress == ownPhysicalAddress):
            if (self._canMove()):
                # send acknowledgement
                self.status = constants.PigConstants.PIG_ALIVE
                newmessage = [constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT,
                           Pig.msgID, self.ip,
                           constants.MessageConstants.ACK_TYPE_POSITIVE, message[2]]
                Pig.msgID += 1
                self.sendAcknowledgement(message[2], newmessage)

            else:
                # alert your immediate neighbours to move and set your status to be dead
                if (message[4] == constants.PigConstants.PIG_SENDER_ORIGINAL):
                    self.status = constants.PigConstants.PIG_DEAD
                # This is the IP address of the caller. Save it so that you can pass Acknowledgement to him.
                self.alertCaller = message[2]
                message1 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER, Pig.msgID, self.ip, ownPhysicalAddress + 1,
                              constants.PigConstants.PIG_SENDER_RELAY]
                Pig.msgID += 1
                message2 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER, Pig.msgID, self.ip,
                              ownPhysicalAddress - 1,
                              constants.PigConstants.PIG_SENDER_RELAY]
                Pig.msgID += 1
                nbrs = self._getNetworkNeighbours()
                for nbr in nbrs:
                    self.sendTakeShelterMessage(nbr, message1)
                    self.sendTakeShelterMessage(nbr, message2)

        else:
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendTakeShelterMessage(nbr, message)

    def sendTakeShelterMessage(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def checkStatus(self):
        return self.status


    def handleHitQueryMessage(self, message):
        pass

    def handleAcknowledgement(self, message):
        receiverIP = message[4]
        if (self.ip == receiverIP):
            if (self.orginalSender == True):
                # This pig started the original alert
                self.status = constants.PigConstants.PIG_EVADED
                ownPhysicalAddress = self._getPhysicalAddress()
                message1 = [constants.MessageConstants.MSGTYPE_I_AM_SAFE,
                       Pig.msgID, self.ip, ownPhysicalAddress + 1]
                Pig.msgID += 1
                message2 = [constants.MessageConstants.MSGTYPE_I_AM_SAFE,
                            Pig.msgID, self.ip, ownPhysicalAddress - 1]
                Pig.msgID += 1
                nbrs = self._getNetworkNeighbours()
                for nbr in nbrs:
                    self.sendIAmSafe(nbr, message1)
                    self.sendIAmSafe(nbr, message2)

            else:
                acknowedgementType = message[3]
                if acknowedgementType == constants.MessageConstants.ACK_TYPE_POSITIVE:
                    self.status = constants.PigConstants.PIG_EVADED
                    if self.alertCaller != -1:
                        message[4] = self.alertCaller
                        message[2] = self.ip
                    nbrs = self._getNetworkNeighbours()
                    for nbr in nbrs:
                        self.sendAcknowledgement(nbr, message)
        else:
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendAcknowledgement(nbr, message)

    def sendAcknowledgement(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        pigProxy.pushMessage(message)

    def _sendAlert(self):
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        ownPhysicalAddress = self._getPhysicalAddress()

        if physicalMap.isEmptySpace(ownPhysicalAddress + 1) or physicalMap.isEmptySpace(ownPhysicalAddress - 1):
            # You are safe
            pass
        else:
            self.status = constants.PigConstants.PIG_DEAD
            self.orginalSender = True
            message1 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                       Pig.msgID, self.ip, ownPhysicalAddress + 1, constants.PigConstants.PIG_SENDER_ORIGINAL]
            Pig.msgID += 1
            message2 = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                       Pig.msgID, self.ip, ownPhysicalAddress - 1, constants.PigConstants.PIG_SENDER_ORIGINAL]
            Pig.msgID += 1
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendTakeShelterMessage(nbr, message1)
                self.sendTakeShelterMessage(nbr, message2)

    def _isGettingAffected(self, targetHit):
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        physicalAddress = self._getPhysicalAddress()
        if (physicalAddress == targetHit) or (physicalAddress == targetHit + 1 and physicalMap.isStone(targetHit)) or (physicalAddress == targetHit - 1 and physicalMap.isStone(targetHit)):
            return True
        return False

    def _canMove(self):
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        ownPhysicalAddress = physicalMap.getPhysicalAddress(self.ip)
        if (physicalMap.isEmptySpace(ownPhysicalAddress - 1) == True or physicalMap.isEmptySpace(ownPhysicalAddress + 1) == True):
            return True
        return False

    def _getPhysicalAddress(self):
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        return physicalMap.getPhysicalAddress(self.ip)

    def _getNetworkNeighbours(self):
        networkURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_NETWORK_MAP
        networkMap = Pyro4.Proxy(networkURI)
        nbrList = networkMap.getNetworkNeighbours(self.ip)
        return nbrList

    def _registerOnServer(self, daemon, nameServer):
        # register this pig with the name server
        uri = daemon.register(self)
        nameServer.register(str(self.ip), uri)
        print("Pig registered with ip: {}".format(self.ip))




# The Message received has following structure:
# 1) Message Type
# 2) Message ID
# 3) Message Caller
# 4...) Other Message params

# Bird_Approaching params
# 1) Hopcount
# 2) Target Coordinate
# 3) Duration

# Take_Shelter params
# 1) Target Coordinate
# 2) Sender type  = {Original, Relay}

# Acknowldegment params
# 1) Acknowledgement type
# 2) Acknowledgement receiver ip

# CheckStatus params
# 1) dictionary = {ip, washit}

# IAmSafe params
# receiver's physical Address