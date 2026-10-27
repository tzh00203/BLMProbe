import tiktoken, re, json
from openai import OpenAI
from __agent_config import label_referee_agent_api_key_gpt, label_referee_agent_api_key_deepseek, label_referee_agent_api_key_DMXapi

def count_chat_tokens(messages, model="gpt-4o-mini"):
    if model.startswith("gpt-4o-mini"):
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    elif model.startswith("gpt-4o") and model != "gpt-4o-mini":
        encoding = tiktoken.encoding_for_model("gpt-4o")
    elif model.startswith("deepseek"):
        encoding = tiktoken.encoding_for_model("deepseek-")
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


class LLMCaller:
    def __init__(self, mode="gpt"):
        """
        Initialize the agent with an OpenAI API key.
        """
        if mode == "gpt":
            self.api_key = label_referee_agent_api_key_gpt
            self.url = "https://api.openai.com/v1/"
            self.model = "gpt-4o"
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.url
            )
            self.DMXapi_key = label_referee_agent_api_key_DMXapi
            self.DMXapi_url = "https://www.dmxapi.com/v1/"
            self.model_DMXapi = "gpt-4o"
            
        elif mode == "deepseek":
            self.api_key = label_referee_agent_api_key_deepseek
            self.url = "https://api.lkeap.cloud.tencent.com/v1/chat/"
            self.model = "deepseek-v3"
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.url
            )
        else: raise("Error! Unsupported model!")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def _send_request_to_llm(self, message: list[dict]) -> str:
       
        max_tokens = 4096

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=message,
                temperature=0.2,
                max_tokens=max_tokens
            )
            res_str = response.choices[0].message.content
            # print(res_str)
            
            return res_str
        except Exception as e:
            return f"Error occurred: {str(e)}"
        
    def _send_request_to_llm_DMXapi(self, message: list[dict]) -> str:

        client = OpenAI(
                api_key=self.DMXapi_key,  # 替换成你的 DMXapi 令牌key
                base_url=self.DMXapi_url,  # 需要改成DMXAPI的中转 https://www.dmxapi.com/v1 ，这是已经改好的。
            )
        max_tokens = 4096
        data = {
            "model": self.model_DMXapi,
            "temperature": 0.2,
            "messages": message
        }

        try:
            chat_completion = client.chat.completions.create(
            
                model=data["model"],  
                messages= data["messages"],
                temperature=data["temperature"],
                max_tokens=4096,
            
            )
            if chat_completion:
            
                return(chat_completion.choices[0].message.content)
            else:
                null_result = "bad response"
                return null_result
        except Exception as e:
            return f"Error occurred: {str(e)}"
