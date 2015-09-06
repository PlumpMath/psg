PORT       = 9091 #TCP/IP port to listen on
BACKLOG    = 100  #If we ignore this many connection attempts, something is wrong!
PING_DELAY = 60 # Seconds between pinging connections
PING_TIMEOUT = 10 # Seconds to wait for a ping response

MAX_GAMES  = 50
GAME_IDS = range(1,MAX_GAMES)