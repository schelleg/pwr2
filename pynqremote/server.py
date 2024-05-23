from concurrent import futures
import grpc

class Server:
    def __init__(self) -> None:
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    def start(self, port):
        self.server.add_insecure_port(f'[::]:{port}')
        self.server.start()

    def stop(self):
        # causes segfault if server started again
        # need to look into this
        self.server.stop(0)