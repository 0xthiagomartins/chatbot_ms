# CLI Documentation

## Table of Contents

- [CLI Documentation](#cli-documentation)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Start a conversation](#start-a-conversation)
    - [Test the CLI](#test-the-cli)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start a conversation

```bash
python3 cli conversation --user_id <user_id> --model <model_name>

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

