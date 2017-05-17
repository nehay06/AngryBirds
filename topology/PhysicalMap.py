import constants.Constants as constants
import random
import Pyro4

@Pyro4.expose
class PhysicalMap:
    """
        This class generates a physical mapping everytime its object is created.
    """


    def __init__(self, daemon, nameServer):

        # IP address to Physical address mapping
        self.IPtoPhysicalMap = {}
        # Physical address to IP address mapping
        self.physicalToIPMap = {}
        # stores the IP address of the nearest pig
        self.nearestPig = -1
        #self._createPhysicalMap()
        self._testing_createMap()
        self.registerOnServer(daemon, nameServer)



    def _createPhysicalMap(self):
        nPigs = constants.MapConstants.NUM_PIGS
        self.physicalMap = [constants.MapConstants.EMPTY_SPACE_ID for x in range(0, constants.MapConstants.MAP_SIZE)]
        self.physicalMap[0: nPigs] = [i for i in range(0, nPigs)]
        self.physicalMap[nPigs: nPigs + constants.MapConstants.NUM_STONES] = [
                                                                                 constants.MapConstants.STONE_ID] * constants.MapConstants.NUM_STONES

        random.shuffle(self.physicalMap)
        for i in range(0, len(self.physicalMap)):
            cur = self.physicalMap[i]

            if (cur != constants.MapConstants.STONE_ID and cur != constants.MapConstants.EMPTY_SPACE_ID):
                if (self.nearestPig == -1):
                    self.nearestPig = cur
                self.IPtoPhysicalMap[cur] = i
                self.physicalToIPMap[i] = cur

        print self.physicalMap


    def getPhysicalAddress(self, ip):
        """
        returns the physical address for a network address
        :param ip: Integer
        :return: Integer
        """
        return self.IPtoPhysicalMap[ip]

    def isStone(self, mac):
        """
        returns boolean if there is a stone at that physical address
        :param mac: Integer
        :return: Boolean
        """
        if (self.physicalMap[mac] == constants.MapConstants.STONE_ID):
            return True
        return False

    def isEmptySpace(self, mac):
        """
        returns boolean if there is a stone at that physical address
        :param mac: Integer
        :return: Boolean
        """
        if (mac < 0):
            return False
        if (self.physicalMap[mac] == constants.MapConstants.EMPTY_SPACE_ID):
            return True
        return False

    def getIPaddress(self, mac):
        """
        returns the Network IP for a physical address
        If none found returns Stone
        :param mac: Integer
        :return: Integer
        """
        if (self.isStone(mac)):
            return constants.MapConstants.STONE_ID
        if (self.isEmptySpace()):
            return constants.MapConstants.EMPTY_SPACE_ID
        return self.physicalToIPMap.get(mac)

    def getNearestPigIP(self):
        """
        returns the Network IP of pig closest to the bird
        :return: Integer
        """
        return self.nearestPig

    def registerOnServer(self, daemon, nameServer):
        # register this pig with the name server
        uri = daemon.register(self)
        nameServer.register("PHYSICAL_MAP", uri)
        print("Network registered with NAME: PHYSICAL_MAP")


    def _testing_createMap(self):
        nPigs = 3
        nStones = 3
        mapSize = 10
        self.physicalMap = [1, -2, 0, 2, 3, 4, -1, -2, -2, -2, -2, -1, -2]
        self.IPtoPhysicalMap[0] = 2
        self.IPtoPhysicalMap[1] = 0
        self.IPtoPhysicalMap[2] = 3
        self.IPtoPhysicalMap[3] = 4
        self.IPtoPhysicalMap[4] = 5

        self.physicalToIPMap[2] = 0
        self.physicalToIPMap[0] = 1
        self.physicalToIPMap[3] = 2
        self.physicalToIPMap[4] = 3
        self.physicalToIPMap[5] = 4


        self.nearestPig = 1
        print self.physicalMap