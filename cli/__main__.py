import os, sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typer import Typer, Option
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.chatbot import ChatbotService

app = Typer()


@app.command()
def conversation(
    user_id: int = Option(..., help="The user ID to start the conversation for"),
    model: str = Option(..., help="The model to use for the conversation"),
):
    chatbot = ChatbotService(user_id=user_id, model=model)
    print("Welcome to the chatbot! Type 'exit' to leave the conversation.")
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


@app.command()
def test():
    print("Test successful")


if __name__ == "__main__":
    app()
