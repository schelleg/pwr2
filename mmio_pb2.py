# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mmio.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmmio.proto\x12\x04mmio\"A\n\x0cWriteRequest\x12\x13\n\x0b\x62\x61seaddress\x18\x01 \x01(\r\x12\x0e\n\x06offset\x18\x02 \x01(\r\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\r\"\x19\n\nWriteReply\x12\x0b\n\x03msg\x18\x01 \x01(\t\"2\n\x0bReadRequest\x12\x13\n\x0b\x62\x61seaddress\x18\x01 \x01(\r\x12\x0e\n\x06offset\x18\x02 \x01(\r\"\x19\n\tReadReply\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\r2e\n\x04MMIO\x12/\n\x05write\x12\x12.mmio.WriteRequest\x1a\x10.mmio.WriteReply\"\x00\x12,\n\x04read\x12\x11.mmio.ReadRequest\x1a\x0f.mmio.ReadReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mmio_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_WRITEREQUEST']._serialized_start=20
  _globals['_WRITEREQUEST']._serialized_end=85
  _globals['_WRITEREPLY']._serialized_start=87
  _globals['_WRITEREPLY']._serialized_end=112
  _globals['_READREQUEST']._serialized_start=114
  _globals['_READREQUEST']._serialized_end=164
  _globals['_READREPLY']._serialized_start=166
  _globals['_READREPLY']._serialized_end=191
  _globals['_MMIO']._serialized_start=193
  _globals['_MMIO']._serialized_end=294
# @@protoc_insertion_point(module_scope)