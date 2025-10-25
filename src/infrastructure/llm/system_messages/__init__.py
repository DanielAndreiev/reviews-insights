from pathlib import Path


def load_system_message(message_name: str) -> str:
    """Load system message from file."""
    messages_dir = Path(__file__).parent
    message_file = messages_dir / f"{message_name}.txt"
    return message_file.read_text(encoding="utf-8")
