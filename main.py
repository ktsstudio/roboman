from roboman import RobomanServer
from bots.kts import KTSBot

if __name__ == "__main__":
    server = RobomanServer(bots=[KTSBot])
    server.start()
