import grpc

class Client:
    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port
        self.channel = grpc.insecure_channel(f"{self.address}:{self.port}")