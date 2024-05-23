from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WriteRequest(_message.Message):
    __slots__ = ["baseaddress", "offset", "data"]
    BASEADDRESS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    baseaddress: int
    offset: int
    data: int
    def __init__(self, baseaddress: _Optional[int] = ..., offset: _Optional[int] = ..., data: _Optional[int] = ...) -> None: ...

class WriteReply(_message.Message):
    __slots__ = ["msg"]
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ["baseaddress", "offset"]
    BASEADDRESS_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    baseaddress: int
    offset: int
    def __init__(self, baseaddress: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ReadReply(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: int
    def __init__(self, data: _Optional[int] = ...) -> None: ...
