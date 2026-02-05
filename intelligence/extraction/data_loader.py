import os


def load_conversation(file_path):
    """
    Load a single conversation from a text file
    Returns a list of message strings
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Conversation file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        messages = [line.strip() for line in file.readlines() if line.strip()]

    return messages


def load_all_conversations(raw_data_path):
    """
    Load all conversation files from raw data folder
    Returns a dictionary {filename: messages}
    """
    conversations = {}

    for file_name in os.listdir(raw_data_path):
        if file_name.endswith(".txt"):
            full_path = os.path.join(raw_data_path, file_name)
            conversations[file_name] = load_conversation(full_path)

    return conversations
