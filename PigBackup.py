import topology.NetworkMap as networkMap
import constants.Constants as constants
import Pyro4
from message.Message import Message



@Pyro4.expose
class Pig:
    msgID = 1
    def __init__(self, ip, daemon, nameServer):
        self.ip = ip
        self.messageCache = []
        self._registerOnServer(daemon, nameServer)
        self.status = constants.PigConstants.PIG_ALIVE


    def pushMessage(self, message):
        if message[1] not in self.messageCache:
            self.messageCache.append(message[1])
            print "Message type: {}, received by :{}, sent by: {}, msgID: {}".format(message[0], self.ip, message[2], message[1])
            if (message[0] == constants.MessageConstants.MSGTYPE_BIRD_APPROACHING):
                self.handleBirdApproachingMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_TAKE_SHELTER):
                self.handleTakeShelterMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_STATUS):
                self.handleStatusMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_WAS_HIT):
                self.handleHitQueryMessage(message)
            elif (message[0] == constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT):
                self.handleAcknowledgement(message)


    def handleBirdApproachingMessage(self, message):
        hopcount = message[3]
        targetHit = message[4]
        duration = message[5]

        if (self._isGettingAffected(targetHit)):
            self._sendAlert(targetHit, duration)

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
                message = [constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT,
                           Pig.msgID, message[2],
                           constants.MapConstants.NUM_PIGS, constants.MessageConstants.ACK_TYPE_POSITIVE]
                Pig.msgID += 1
                self.sendAcknowledgement(message[2], message)
            else:
                message = [constants.MessageConstants.MSGTYPE_ACKNOWLEDGEMENT,
                           Pig.msgID, message[2],
                           constants.MapConstants.NUM_PIGS, constants.MessageConstants.ACK_TYPE_NEGATIVE]
                Pig.msgID += 1
                self.sendAcknowledgement(message[2], message)

        else:
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendTakeShelterMessage(nbr, message)

    def sendTakeShelterMessage(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        message[2] = self.ip
        pigProxy.pushMessage(message)

    def handleCheckStatusMessage(self, message):
        if self.status == constants.PigConstants.PIG_DEAD:
            # send the status to caller that you are dead
            pass

    def sendCheckStatusMessage(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        message[2] = self.ip
        pigProxy.pushMessage(message)

    def handleHitQueryMessage(self, message):
        pass

    def handleAcknowledgement(self, message):
        acknowedgementType = message[3]
        if acknowedgementType == constants.MessageConstants.ACK_TYPE_POSITIVE:
            self.status = constants.PigConstants.PIG_ALIVE
            nbrs = self._getNetworkNeighbours()
            for nbr in nbrs:
                self.sendAcknowledgement(nbr, message)

    def sendAcknowledgement(self, nbr, message):
        if (message[1] not in self.messageCache):
            self.messageCache.append(message[1])
        pigURI = constants.UriConstants.URI_PYRONAME + str(nbr)
        pigProxy = Pyro4.Proxy(pigURI)
        message[2] = self.ip
        pigProxy.pushMessage(message)

    def _sendAlert(self, targetHit, duration):
        physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
        physicalMap = Pyro4.Proxy(physicalMapURI)
        ownPhysicalAddress = self._getPhysicalAddress()

        if (ownPhysicalAddress == targetHit):
            if physicalMap.isEmptySpace(targetHit + 1) or physicalMap.isEmptySpace(targetHit - 1):
                # The scenario is W/P', P(B), _  or _, P(B), W/P'
                # You are safe
                pass
            else:
                # The scenario is P'/W, P(B), W/P'
                self.status = constants.PigConstants.PIG_DEAD
                message = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                           Pig.msgID, self.ip, targetHit + 1]
                nbrs = self._getNetworkNeighbours()
                Pig.msgID += 1;
                for nbr in nbrs:
                    self.sendTakeShelterMessage(nbr, message)

                message[3] = targetHit - 1
                message[1] = Pig.msgID
                Pig.msgID += 1
                for nbr in nbrs:
                    self.sendTakeShelterMessage(nbr, message)

        elif (ownPhysicalAddress == targetHit + 1):
            if physicalMap.isEmptySpace(ownPhysicalAddress + 1):
                # The scenario is W(B), P, _
                # You are safe again.
                pass

            else:
                # The scenario is W(B), P, P'
                # send message to move for any pig at ownPhysicalAddress + 1.
                self.status = constants.PigConstants.PIG_DEAD
                message = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                           Pig.msgID, self.ip,
                           constants.MapConstants.NUM_PIGS, ownPhysicalAddress + 1]
                nbrs = self._getNetworkNeighbours()
                Pig.msgID += 1
                for nbr in nbrs:
                    self.sendTakeShelterMessage(nbr, message)

        elif (ownPhysicalAddress == targetHit - 1):
            if physicalMap.isEmptySpace(ownPhysicalAddress - 1):
                # The scenario is _ , P, S(B)
                # You are safe again
                pass
            else:
                # The scenario is P', P, S(B)
                # send message to move for any pig at ownPhysicalAddress - 1
                self.status = constants.PigConstants.PIG_DEAD
                message = [constants.MessageConstants.MSGTYPE_TAKE_SHELTER,
                           Pig.msgID, self.ip,
                           constants.MapConstants.NUM_PIGS, targetHit]
                nbrs = self._getNetworkNeighbours()
                Pig.msgID += 1;
                for nbr in nbrs:
                    self.sendTakeShelterMessage(nbr, message)

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

# Acknowldegment params
# 1) Acknowledgement type

# CheckStatus params
# 1) dictionary = {ip, washit}