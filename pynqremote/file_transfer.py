import os
from concurrent import futures

import grpc
import time
import hashlib

from . import chunk_pb2, chunk_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB
BINFILE_NAME = 'overlay.bin'
FIRMWARE_PATH = '/lib/firmware/' + BINFILE_NAME

BS_FPGA_MAN = "/sys/class/fpga_manager/fpga0/firmware"
BS_FPGA_MAN_FLAGS = "/sys/class/fpga_manager/fpga0/flags"

def get_sha256_file(filepath):
    BLOCK_SIZE = 1024
    m = hashlib.sha256()
    if os.path.exists(filepath):
        with open(filepath,"rb") as myfile:
            while True:
                data = myfile.read(BLOCK_SIZE)
                if not data:
                    return m 
                m.update(data)
        
def get_file_chunks(filename):
    with open(filename, 'rb') as f:
        while True:
            piece = f.read(CHUNK_SIZE)
            if len(piece) == 0:
                return
            yield chunk_pb2.Chunk(hash=get_sha256_file(filename).hexdigest(),buffer=piece)

def save_chunks_to_file(chunks, filename):
    # write chunks to file
    with open(filename, 'wb') as f:
        for chunk in chunks:
            if chunk.hash != 0:
                hash_data = chunk.hash
            f.write(chunk.buffer)
    # integrity check - compute and compare hashes
    if hash_data == get_sha256_file(filename).hexdigest():
        load_bitstream()
        return True
    else:
        return False

def load_bitstream():
        with open(BS_FPGA_MAN_FLAGS, 'w') as fd:
            fd.write(str(0))
        with open(BS_FPGA_MAN, 'w') as fd:
            fd.write(BINFILE_NAME)

class FileClient:
    def __init__(self, channel):
        self.stub = chunk_pb2_grpc.FileServerStub(channel)

    def upload(self, in_file_name):
        # check if file exists and has read permissions
        if os.path.isfile(in_file_name) and os.access(in_file_name, os.R_OK):
            print("[CLIENT] File exists and is readable")
        else:
            print("[CLIENT] Either the file is missing or not readable")
            exit()

        chunks_generator = get_file_chunks(in_file_name)
        response = self.stub.upload(chunks_generator)
        assert response.length == os.path.getsize(in_file_name)
        print(f"[SERVER] {response.msg}")
        print(f"[SERVER] {response.length} bytes received")

    def download(self, target_name, out_file_name):
        response = self.stub.download(chunk_pb2.Request(name=target_name))
        save_chunks_to_file(response, out_file_name)

class FileServicer(chunk_pb2_grpc.FileServerServicer):
    def upload(self, request_iterator, context):
        if save_chunks_to_file(request_iterator, FIRMWARE_PATH):
            return chunk_pb2.Reply(msg="Data received and verified.",length=os.path.getsize(FIRMWARE_PATH))
        else:
            return chunk_pb2.Reply(msg="Data received but verification failed!",length=os.path.getsize(FIRMWARE_PATH))

    def download(self, request, context):
        if request.name:
            return get_file_chunks(FIRMWARE_PATH)

class FileServer(FileServicer):
    def __init__(self, server):
        self.servicer = FileServicer()
        chunk_pb2_grpc.add_FileServerServicer_to_server(self.servicer, server.server)

    # def upload(self, request_iterator):
    #     self.servicer.upload(request_iterator)

    # def download(self, request):
    #     self.servicer.download(request)        