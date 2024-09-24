from nameko.rpc import rpc
from langchain_core.messages import BaseMessageChunk
import uuid
from .router import Router


class BaseRpcServer:
    _router: Router = None

    def __init__(self):
        # Dictionary to hold stream states
        self.streams = {}

    @rpc
    def invoke(self, runnable_id, *args, **kwargs):
        runnable = self._router.get(runnable_id)
        return runnable.invoke(*args, **kwargs)

    @rpc
    def batch(self, runnable_id, *args, **kwargs):
        runnable = self._router.get(runnable_id)
        return runnable.batch(*args, **kwargs)

    @rpc
    def start_stream(self, runnable_id, input: str):
        stream_id = str(uuid.uuid4())
        runnable = self._router.get(runnable_id)
        self.streams[stream_id] = runnable.stream(input)
        return stream_id

    @rpc
    def get_next_chunk(self, stream_id):
        stream = self.streams.get(stream_id)
        if not stream:
            raise ValueError("Invalid stream ID")
        try:
            chunk: BaseMessageChunk = next(stream)
        except StopIteration:
            return {"done": True}
        return {"done": False, "chunk": chunk.to_json()}
