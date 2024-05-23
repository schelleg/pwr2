import grpc
from . import mmio_pb2, mmio_pb2_grpc
import os
import numpy as np

grpc.logging.basicConfig(level=grpc.logging.INFO)

class MMIO:
    def __init__(self, channel, baseaddress) -> None:
        self.stub = mmio_pb2_grpc.MMIOStub(channel)
        self.baseaddress = baseaddress

    def write(self, offset, data):
        request = mmio_pb2.WriteRequest(baseaddress=self.baseaddress,
                                        offset=offset, data=data)
        self.stub.write(request)
    
    def read(self, offset):
        request = mmio_pb2.ReadRequest(baseaddress=self.baseaddress,
                                       offset=offset)
        response = self.stub.read(request)
        return response.data

class MMIOServicer(mmio_pb2_grpc.MMIOServicer):
    def mmap(self, baseaddress, length=4):
        import mmap
        
        euid = os.geteuid()
        if euid != 0:
            raise EnvironmentError("Root permissions required.")
        
        # Align the base address with the pages
        virt_base = baseaddress & ~(mmap.PAGESIZE - 1)
        
        # Calculate base address offset w.r.t the base address
        virt_offset = baseaddress - virt_base
        
        # Open file and mmap
        mmap_file = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        mem = mmap.mmap(
            mmap_file,
            length + virt_offset,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=virt_base,
        )
        os.close(mmap_file)
        array = np.frombuffer(mem, np.uint32, length >> 2, virt_offset)
        return array
    
    def write(self, request, context):
        baseaddress = request.baseaddress
        offset = request.offset
        data = request.data

        array = self.mmap(baseaddress)
        idx = offset >> 2
        array[idx] = np.uint32(data)

        return mmio_pb2.WriteReply(msg="received")
    
    def read(self, request, context):
        baseaddress = request.baseaddress
        offset = request.offset

        array = self.mmap(baseaddress)
        idx = offset >> 2
        response = mmio_pb2.ReadReply()
        response.data = ((int(array[idx + 1])) << 32) + lsb
        return response

class MMIOServer(MMIOServicer):
    def __init__(self, server) -> None:
        self.servicer = MMIOServicer()
        mmio_pb2_grpc.add_MMIOServicer_to_server(self.servicer, server.server)