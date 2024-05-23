import base64
import functools
import struct
from urllib.parse import unquote

# import grpc


_HEADER_FORMAT = ">BI"
_HEADER_LENGTH = struct.calcsize(_HEADER_FORMAT)


def _pack_header_flags(trailers, compressed):
    return (trailers << 7) | (compressed)


def _unpack_header_flags(flags):
    trailers = 1 << 7
    compressed = 1

    return bool(trailers & flags), bool(compressed & flags)


def wrap_message(trailers, compressed, message):
    return (
        struct.pack(
            _HEADER_FORMAT, _pack_header_flags(trailers, compressed), len(message)
        )
        + message
    )


def b64_wrap_message(trailers, compressed, message):
    return base64.b64encode(wrap_message(trailers, compressed, message))


def unwrap_message(message):
    flags, length = struct.unpack(_HEADER_FORMAT, message[:_HEADER_LENGTH])
    data = message[_HEADER_LENGTH : _HEADER_LENGTH + length]

    if length != len(data):
        raise ValueError()

    trailers, compressed = _unpack_header_flags(flags)

    return trailers, compressed, data


def b64_unwrap_message(message):
    return unwrap_message(base64.b64decode(message))


def unwrap_message_stream(stream):
    data = stream.read(_HEADER_LENGTH)

    while data:
        flags, length = struct.unpack(_HEADER_FORMAT, data)
        trailers, compressed = _unpack_header_flags(flags)

        yield trailers, compressed, stream.read(length)

        if trailers:
            break

        data = stream.read(_HEADER_LENGTH)


async def unwrap_message_stream_async(stream):
    data = await stream.readexactly(_HEADER_LENGTH)

    while data:
        flags, length = struct.unpack(_HEADER_FORMAT, data)
        trailers, compressed = _unpack_header_flags(flags)

        yield trailers, compressed, await stream.readexactly(length)

        if trailers:
            break

        data = await stream.readexactly(_HEADER_LENGTH)


async def unwrap_message_asgi(receive, decoder=None):
    buffer = bytearray()
    waiting = False
    flags = None
    length = None

    while True:
        event = await receive()
        assert event["type"].startswith("http.")

        if decoder:
            chunk = decoder(event["body"])
        else:
            chunk = event["body"]

        buffer += chunk

        if len(buffer) >= _HEADER_LENGTH:
            if not waiting:
                flags, length = struct.unpack(_HEADER_FORMAT, buffer[:_HEADER_LENGTH])

            if len(buffer) >= _HEADER_LENGTH + length:
                waiting = False
                data = buffer[_HEADER_LENGTH : _HEADER_LENGTH + length]
                trailers, compressed = _unpack_header_flags(flags)

                yield trailers, compressed, data
                buffer = buffer[_HEADER_LENGTH + length :]
            else:
                waiting = True

        if not event.get("more_body"):
            break


b64_unwrap_message_asgi = functools.partial(
    unwrap_message_asgi, decoder=base64.b64decode
)


def pack_trailers(trailers):
    message = []
    for k, v in trailers:
        k = k.lower()
        message.append(f"{k}: {v}\r\n".encode("ascii"))
    return b"".join(message)


def unpack_trailers(message):
    trailers = []
    for line in message.decode("ascii").splitlines():
        k, v = line.split(":", 1)
        v = v.strip()

        trailers.append((k, v))
    return trailers


def encode_headers(metadata):
    for header, value in metadata:
        if isinstance(value, bytes):
            if not header.endswith("-bin"):
                raise ValueError("binary headers must have the '-bin' suffix")

            value = base64.b64encode(value).decode("ascii")

        if isinstance(header, bytes):
            header = header.decode("ascii")

        yield header, value



from enum import Enum
class Status(Enum):
    """Predefined gRPC status codes represented as enum

    See also: https://github.com/grpc/grpc/blob/master/doc/statuscodes.md
    """
    #: The operation completed successfully
    OK = 0
    #: The operation was cancelled (typically by the caller)
    CANCELLED = 1
    #: Generic status to describe error when it can't be described using
    #: other statuses
    UNKNOWN = 2
    #: Client specified an invalid argument
    INVALID_ARGUMENT = 3
    #: Deadline expired before operation could complete
    DEADLINE_EXCEEDED = 4
    #: Some requested entity was not found
    NOT_FOUND = 5
    #: Some entity that we attempted to create already exists
    ALREADY_EXISTS = 6
    #: The caller does not have permission to execute the specified operation
    PERMISSION_DENIED = 7
    #: Some resource has been exhausted, perhaps a per-user quota, or perhaps
    #: the entire file system is out of space
    RESOURCE_EXHAUSTED = 8
    #: Operation was rejected because the system is not in a state required
    #: for the operation's execution
    FAILED_PRECONDITION = 9
    #: The operation was aborted
    ABORTED = 10
    #: Operation was attempted past the valid range
    OUT_OF_RANGE = 11
    #: Operation is not implemented or not supported/enabled in this service
    UNIMPLEMENTED = 12
    #: Internal errors
    INTERNAL = 13
    #: The service is currently unavailable
    UNAVAILABLE = 14
    #: Unrecoverable data loss or corruption
    DATA_LOSS = 15
    #: The request does not have valid authentication credentials for the
    #: operation
    UNAUTHENTICATED = 16



class WebRpcError(Exception):
    _code_to_enum = {code.value: code for code in Status}  # type: ignore

    def __init__(self, code, details, *args, **kwargs):
        super(WebRpcError, self).__init__(*args, **kwargs)

        self._code = code
        self._details = details

    @classmethod
    def from_metadata(cls, trailers):
        status = int(trailers["grpc-status"])
        details = trailers.get("grpc-message")

        code = cls._code_to_enum[status]

        return cls(code, details)

    def __str__(self):
        return "WebRpcError(status_code={}, details='{}')".format(
            self._code, self._details
        )

    def code(self):
        return self._code

    def details(self):
        return self._details


def raise_for_status(headers, trailers=None):
    if trailers:
        metadata = dict(trailers)
    else:
        metadata = headers

    if "grpc-status" in metadata and metadata["grpc-status"] != "0":
        metadata = metadata.copy()

        if "grpc-message" in metadata:
            metadata["grpc-message"] = unquote(metadata["grpc-message"])

        raise WebRpcError.from_metadata(metadata)


_timeout_units = {
    b"H": 3600.0,
    b"M": 60.0,
    b"S": 1.0,
    b"m": 1 / 1000.0,
    b"u": 1 / 1000000.0,
    b"n": 1 / 1000000000.0,
}


def parse_timeout(value):
    units = value[-1:]
    coef = _timeout_units[units]
    count = int(value[:-1])
    return count * coef


def serialize_timeout(seconds):
    if seconds % 3600 == 0:
        value = seconds // 3600
        units = "H"
    elif seconds % 60 == 0:
        value = seconds // 60
        units = "M"
    elif seconds % 1 == 0:
        value = seconds
        units = "S"
    elif seconds * 1000 % 1 == 0:
        value = seconds * 1000
        units = "m"
    elif seconds * 1000000 % 1 == 0:
        value = seconds * 1000000
        units = "u"
    else:
        value = seconds * 1000000000
        units = "n"

    return f"{int(value)}{units}"
