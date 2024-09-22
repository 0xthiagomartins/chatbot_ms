import os, sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typer import Typer, Option
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print
from src.chatbot import ChatbotService
from src import orm

app = Typer()


def display_message(message: str):
    # I want a horizontal line
    print(f"[bold]{message['type']}[/bold]: {message['content']}")
    print("[bold]-[/bold]" * 100)


def start_chatting(chatbot: ChatbotService, streamed: bool = False):
    if not streamed:
        while True:
            message = Prompt.ask("You: ", default="", show_default=False)
            if message.lower() == "exit":
                break
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Thinking...", total=None)
                response = chatbot.send(message=message)
            print(f"Chatbot: {response}")
    else:
        while True:
            message = Prompt.ask("You: ", default="", show_default=False)
            if message.lower() == "exit":
                break
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Thinking...", total=None)
                for chunk in chatbot.send_streamed(message):
                    print(chunk[0], end="", flush=True)


@app.command()
def start_conversation(
    user_id: int = Option(..., help="The user ID to start the conversation for"),
    model: str = Option(..., help="The model to use for the conversation"),
    conversation_id: int = Option(
        None, help="The conversation ID to continue (optional)"
    ),
):
    chatbot = ChatbotService(
        user_id=user_id, model=model, conversation_id=conversation_id
    )
    print("Welcome to the chatbot! Type 'exit' to leave the conversation.")
    if conversation_id:
        print(
            f"Continuing conversation with ID: {conversation_id} - {model} - {user_id}"
        )
        print("[bold]-[/bold]" * 100)
        for message in chatbot.conversation.get("messages", []):
            display_message(message)
    start_chatting(chatbot)


@app.command()
def start_streamed_conversation(
    user_id: int = Option(..., help="The user ID to start the conversation for"),
    model: str = Option(..., help="The model to use for the conversation"),
    conversation_id: int = Option(
        None, help="The conversation ID to continue (optional)"
    ),
):
    chatbot = ChatbotService(
        user_id=user_id, model=model, conversation_id=conversation_id
    )
    print("Welcome to the chatbot! Type 'exit' to leave the conversation.")
    if conversation_id:
        print(
            f"Continuing conversation with ID: {conversation_id} - {model} - {user_id}"
        )
        print("[bold]-[/bold]" * 100)
        for message in chatbot.conversation.get("messages", []):
            display_message(message)
    start_chatting(chatbot, streamed=True)


@app.command()
def list_conversations(
    user_id: int = Option(..., help="The user ID to list conversations for")
):
    conversations = orm.conversations.list(
        filter={"user_id": user_id, "archived": False},
        order={"updated_at": "desc"},
        mode="all",
    )
    for conversation in conversations:
        print(
            {
                "id": conversation["id"],
                "title": conversation["title"],
                "updated_at": conversation["updated_at"],
            }
        )


@app.command()
def test():
    print("Test successful")


if __name__ == "__main__":
    app()
