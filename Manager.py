import Pyro4
import constants.Constants as constants
from bird.Bird import Bird
import time


physicalMapURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_PHYSICAL_MAP
physicalMap = Pyro4.Proxy(physicalMapURI)

networkURI = constants.UriConstants.URI_PYRONAME + constants.UriConstants.URI_NETWORK_MAP
networkMap = Pyro4.Proxy(networkURI)

nearestPigIP = physicalMap.getNearestPigIP()
print nearestPigIP

# get flight details from bird
(duration, destination) = Bird().getFlightDetails()
print "Bird destination: {}".format(destination)

nearestPigURI = constants.UriConstants.URI_PYRONAME + str(nearestPigIP)
nearestPig = Pyro4.Proxy(nearestPigURI)  # use name server object lookup uri shortcut

# message is a tuple
message = [constants.MessageConstants.MSGTYPE_BIRD_APPROACHING, constants.MessageConstants.DEFAULT_MESSAGE_ID, constants.MessageConstants.ID_MANAGER, constants.MapConstants.NUM_PIGS, destination, duration]
nearestPig.pushMessage(message)

# start timer
time.sleep(4)
# query status
for pig in range(0, constants.MapConstants.NUM_PIGS):
    pigURI = constants.UriConstants.URI_PYRONAME + str(pig)
    pigProxy = Pyro4.Proxy(pigURI)
    print "Status of pig {} :  {}".format(pig, pigProxy.checkStatus())




# The Message received has following structure:
# 1) Message Type
# 2) Message ID
# 3) Message Caller
# 4) Message params

# Bird_Approaching
# 1) Hopcount
# 2) Destination
# 3) Duration

# Take_Shelter