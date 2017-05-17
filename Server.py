import Pyro4
import constants.Constants as constants
import utils.Utils as utils
from topology.NetworkMap import NetworkMap
from bird.Bird import Bird
from topology.PhysicalMap import PhysicalMap
from pigs.Pig import Pig


daemon = Pyro4.Daemon()
# finds the name server
nameServer = Pyro4.locateNS(constants.ServerConstants.SERVER_HOST, constants.ServerConstants.SERVER_PORT)

# The network map will be constant for all iterations
networkMap = NetworkMap(daemon, nameServer)

# Pigs are placed
physicalMap = PhysicalMap(daemon, nameServer)

#Make pigs
for pig in range(0, constants.MapConstants.NUM_PIGS):
    Pig(pig, daemon, nameServer)

print "all pigs registered"

daemon.requestLoop()


# start request loop

#end of iteration



# terminate server
