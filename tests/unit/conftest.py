import threading
from concurrent.futures import ThreadPoolExecutor

import grpc
import pytest
from flexlogger.automation import ChannelSpecificationDocument, FlexLoggerError
from flexlogger.automation.proto import ChannelDataStream_pb2, ChannelDataStream_pb2_grpc
from flexlogger.automation.proto.Identifiers_pb2 import ElementIdentifier


class FakeChannelDataStreamServicer(ChannelDataStream_pb2_grpc.ChannelDataStreamServicer):
    """A scriptable stand-in for the FlexLogger ChannelDataStream service."""

    def __init__(self):
        self.stream_requests = []
        self.metadata_requests = []
        self.stream_messages = []
        self.channel_metadata = []
        self.abort_status = None
        self.keep_stream_open = False
        self.client_disconnected = threading.Event()

    def StreamChannelData(self, request, context):
        self.stream_requests.append(request)
        if not context.add_callback(self.client_disconnected.set):
            self.client_disconnected.set()
        for message in self.stream_messages:
            yield message
        if self.abort_status is not None:
            context.abort(*self.abort_status)
        if self.keep_stream_open:
            self.client_disconnected.wait(timeout=10)

    def GetChannelMetadata(self, request, context):
        self.metadata_requests.append(request)
        if self.abort_status is not None:
            context.abort(*self.abort_status)
        return ChannelDataStream_pb2.GetChannelMetadataResponse(channels=self.channel_metadata)


class ApplicationClosedSwitch:
    """Stands in for the application's closed check; raises once closed."""

    def __init__(self):
        self.is_closed = False

    def __call__(self):
        if self.is_closed:
            raise FlexLoggerError("The application is closed.")


@pytest.fixture
def servicer():
    return FakeChannelDataStreamServicer()


@pytest.fixture
def grpc_channel(servicer):
    server = grpc.server(ThreadPoolExecutor(max_workers=4))
    ChannelDataStream_pb2_grpc.add_ChannelDataStreamServicer_to_server(servicer, server)
    port = server.add_insecure_port("localhost:0")
    server.start()
    channel = grpc.insecure_channel("localhost:%d" % port)
    yield channel
    channel.close()
    server.stop(None)


@pytest.fixture
def application_closed_switch():
    return ApplicationClosedSwitch()


@pytest.fixture
def channel_specification_document(grpc_channel, application_closed_switch):
    identifier = ElementIdentifier(project_id="project", file_name="channels.lcspec")
    return ChannelSpecificationDocument(grpc_channel, application_closed_switch, identifier)
