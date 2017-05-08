from bots.kts import KTSBot
from roboman.server import RobomanServer

if __name__ == "__main__":
    server = RobomanServer(bots=[KTSBot])
    server.start()
