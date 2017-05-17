import constants.Constants as constants
import utils.Utils as utils

class Bird:

    def __init__(self):
        #self._makeBird()
        self._testing_makeBird()

    def _makeBird(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.duration = utils.getInRange(constants.BirdConstants.MIN_DURATION, constants.BirdConstants.MAX_DURATION)
        self.destination = utils.getInRange(constants.BirdConstants.MIN_DESTINATION,
                                            constants.BirdConstants.MAX_DESTINATION)

    def _testing_makeBird(self):
        self.id = constants.BirdConstants.DEFAULT_BIRD_ID
        self.destination = 6
        self.duration = 100


    def getFlightDetails(self):
        flightDetails = (self.duration, self.destination)
        return flightDetails


