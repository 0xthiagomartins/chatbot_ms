# Create a RemoteRunnable that can be used to call the service from others nameko services

from typing import List
from nameko.rpc import RpcProxy


class RemoteRunnable:
    def __init__(self, rpc: RpcProxy, chain_id: str):
        self.rpc = rpc
        self.chain_id = chain_id

    def invoke(self, input: str):
        return self.rpc.router(self.chain_id, "invoke", input)

    def batch(self, inputs: List[str]):
        return self.rpc.router(self.chain_id, "batch", inputs)

    def stream(self, input: str):
        stream_id = self.rpc.start_stream(self.chain_id, input)
        for chunk in self.rpc.get_next_chunk(stream_id):
            if chunk["done"]:
                break
            yield chunk["chunk"]

    async def ainvoke(self, input: str):
        return await self.rpc.arouter(self.chain_id, "ainvoke", input)

    async def abatch(self, inputs: List[str]):
        return await self.rpc.arouter(self.chain_id, "abatch", inputs)

    async def astream(self, input: str):
        return await self.rpc.arouter(self.chain_id, "astream", input)


"""
Sample client usage


rpc_genai = RemoteRunnable(RpcProxy("langchain"), "genai")

for chunk in rpc_genai.stream("Hello, world!"):
    print(chunk["content"], chunk["type"])

"""
