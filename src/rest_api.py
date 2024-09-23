# Create a RestAPI using FastAPI and langserve that will be used to interact with the chatbot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from .chatbot import ChatbotService


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
chain = ChatbotService(
    user_id=1, model="gpt-3.5-turbo", conversation_id=1
).__get_chain()

add_routes(app, chain, "/chat")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
