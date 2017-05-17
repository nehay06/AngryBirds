# This module contains all the constants in python

class BirdConstants:
    # The max number of bird in the game
    MAX_NUMBER_OF_BIRDS = 3
    # The range within bird can fall
    MAX_DESTINATION = 10
    MIN_DESTINATION = 0

    # The main amd max duration of flight of bird
    MIN_DURATION = 1000
    MAX_DURATION = 1000000

    # Default bird id
    DEFAULT_BIRD_ID = 007

class PigConstants:
    # Maximum neighbours of the pig
    MAX_PIG_NEIGHBOURS = 2

    #Pig status
    PIG_ALIVE = 1
    PIG_DEAD = 2
    PIG_EVADED = 3

    PIG_SENDER_ORIGINAL = 4
    PIG_SENDER_RELAY = 5

class MapConstants:
    # Size of maximum physical map
    MAP_SIZE = 13
    # Number of pigs in physical map
    NUM_PIGS = 5
    # Number of stones in physical ma
    NUM_STONES = 3
    # Sentinel value to represent Stone and Empty space
    STONE_ID = -1
    EMPTY_SPACE_ID = -2

class MessageConstants:

    MSGTYPE_BIRD_APPROACHING = 1
    MSGTYPE_TAKE_SHELTER = 2
    MSGTYPE_STATUS = 3
    MSGTYPE_STATUS_ALL = 4
    MSGTYPE_ACKNOWLEDGEMENT = 6
    MSGTYPE_I_AM_SAFE = 7
    MSGTYPE_INVALID = -1

    ACK_TYPE_POSITIVE = 777
    ACK_TYPE_NEGATIVE = 888

    MSG_STRING_WAS_HIT = "WAS HIT"

    BIRD_APPROACHING_RECEIVED = 1
    BIRD_APPROACHING_NOT_RECEIVED = 2
    ID_MANAGER = 1234;
    DEFAULT_MESSAGE_ID = 0;

class ServerConstants:
    SERVER_PORT = 9090
    SERVER_HOST = "localhost"

class UriConstants:
    URI_PYRONAME = "PYRONAME:"
    URI_NETWORK_MAP = "NETWORK_MAP"
    URI_PHYSICAL_MAP = "PHYSICAL_MAP"