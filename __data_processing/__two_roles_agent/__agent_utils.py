import tiktoken

def count_chat_tokens(messages, model="gpt-4o-mini"):
    if model.startswith("gpt-4o-mini"):
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    elif model.startswith("gpt-4o"):
        encoding = tiktoken.encoding_for_model("gpt-4o")
    else:
        raise ValueError("Unsupported model")

    tokens_per_message = 4
    tokens_per_system_message = 1
    total_tokens = 0
    message_tokens = []

    for message in messages:
        tokens = encoding.encode(message["content"])
        total_tokens += tokens_per_message + len(tokens)
        if message["role"] == "system":
            total_tokens += tokens_per_system_message
        message_tokens.append((message, tokens))

    return total_tokens, message_tokens

def truncate_chat_messages(messages, max_tokens, model="gpt-4o-mini"):
    total_tokens, message_tokens = count_chat_tokens(messages, model)
    if total_tokens <= max_tokens:
        return messages

    encoding = tiktoken.encoding_for_model(model)
    truncated_messages = []
    truncated_total_tokens = 0

    for message, tokens in message_tokens:
        if truncated_total_tokens + len(tokens) + 4 > max_tokens:
            remaining_tokens = max_tokens - truncated_total_tokens - 4
            tokens = tokens[:remaining_tokens]
            message["content"] = encoding.decode(tokens)
            truncated_messages.append(message)
            break
        else:
            truncated_messages.append(message)
            truncated_total_tokens += len(tokens) + 4

    return truncated_messages