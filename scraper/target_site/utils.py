CHUNK_SIZE = 1000


def chunk_content(content: str, size: int = CHUNK_SIZE) -> list[str]:
    if not content:
        return []
    return [content[index : index + size] for index in range(0, len(content), size)]
