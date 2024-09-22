# CLI Documentation

## Table of Contents

- [CLI Documentation](#cli-documentation)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Start a conversation](#start-a-conversation)
      - [Optional arguments](#optional-arguments)
    - [Test the CLI](#test-the-cli)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start a conversation

#### Optional arguments

- `--user-id <user_id>`: The user ID to start the conversation for.
- `--model <model_name>`: The model to use for the conversation. Available models: `gpt-3.5-turbo`, `claude-3-5-sonnet-20240620`, `gemini-1.5-flash`, `gemini-1.5-pro`.
- `--conversation-id <conversation_id>`: The conversation ID to continue. [Optional]

```bash
python3 cli start-conversation --user-id <user_id> --model <model_name> --conversation-id <conversation_id> (optional)

>>> Welcome to the chatbot! Type 'exit' to leave the conversation.
>>> You: Hello, how are you?
>>> Chatbot: I'm fine, thank you! How can I help you today?
>>> You: I need help with my taxes.
>>> Chatbot: I'm sorry, I can't help with that.
>>> You: Can you tell me a joke?
>>> Chatbot: Why don't scientists trust atoms? Because they make up everything!
>>> You: That's not funny.
>>> Chatbot: I'm sorry, I'm not very good at jokes.
>>> You: exit
```

### Test the CLI

```bash
python3 cli test

>>> Test successful
```

