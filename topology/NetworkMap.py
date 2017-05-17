import constants.Constants as constants
import Pyro4

@Pyro4.expose
class NetworkMap:

    def __init__(self, daemon, nameServer):
        self.nPigs = constants.MapConstants.NUM_PIGS
        self.networkMap = {}
        self.createMap()
        self.registerOnServer(daemon, nameServer)

    def createMap(self):
        for i in range(0, self.nPigs):
            cur = i
            prev = (self.nPigs + i - 1) % self.nPigs
            next = (self.nPigs + i + 1) % self.nPigs
            self.networkMap[cur] = [prev, next]


    def getNetworkNeighbours(self, ip):
        """
        returns the logical network neighbours for an IP
        :param ip: Integer
        :return: List
        """
        nbrList = self.networkMap[ip]
        return nbrList


    def registerOnServer(self, daemon, nameServer):
        # register this pig with the name server
        uri = daemon.register(self)
        nameServer.register("NETWORK_MAP", uri)
        print("Network registered with NAME: NETWORK_MAP")