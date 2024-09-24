from nameko.rpc import rpc
from nameko.exceptions import RemoteError
import asyncio
from ...sample.routers import Router
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class LangChainService:
    """
    LangServe helps developers deploy LangChain runnables and chains as a RPC API.

    This library is integrated with nameko and uses pydantic for data validation.
    """

    name = "langchain"
    _router = Router()
    _router.add()
    _router.add(
        "genai",
        ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
        ),
    )

    @rpc
    def router(self, chain_id: str, method: str, *args, **kwargs):
        """
        Route RPC calls to the appropriate chain and method.

        :param chain_id: Identifier of the chain.
        :param method: Method to invoke on the chain.
        :param args: Positional arguments for the method.
        :param kwargs: Keyword arguments for the method.
        :return: Result of the method invocation.
        """
        if chain_id not in self._router.__chains:
            raise RemoteError("ChainNotFound", f"Chain with ID '{chain_id}' not found.")

        chain = self._router.get(chain_id)

        # Handle schema-related methods
        if method in ["input_schema", "output_schema", "config_schema"]:
            schema = self._router.get_schema(chain_id).get(method)
            if schema is None:
                raise RemoteError(
                    "SchemaNotFound",
                    f"Schema '{method}' not found for chain '{chain_id}'.",
                )
            return schema

        # Check if the chain has the requested method
        if not hasattr(chain, method):
            raise RemoteError(
                "MethodNotFound", f"Method '{method}' not found in chain '{chain_id}'."
            )

        method_func = getattr(chain, method)

        try:
            if asyncio.iscoroutinefunction(method_func):
                # If the method is asynchronous, run it
                result = asyncio.run(method_func(*args, **kwargs))
            else:
                result = method_func(*args, **kwargs)
            return result
        except Exception as e:
            raise RemoteError("InvocationError", str(e))
