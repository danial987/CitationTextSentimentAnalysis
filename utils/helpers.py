def split_text_into_chunks(text, max_tokens=3000, overlap=0):
    """
    Split text into smaller chunks for processing, with optional overlapping.
    """
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = current_chunk[-overlap:] + [sentence]
            current_tokens = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks
