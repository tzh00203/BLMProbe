import json
import requests
from __two_roles_agent.__agent_utils import truncate_chat_messages
import __agent_config
# API_KEY = __agent_config.label_referee_agent_api_key

class LabelRefereeAgent:
    """
    A Label Referee Agent for evaluating and synthesizing Internet-connected device labels.
    It leverages GPT to referee five ranked labels and determine if they describe a unique device.
    """

    def __init__(self, api_key):
        """
        Initialize the agent with an OpenAI API key.
        """
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _send_request_to_gpt(self, prompt):
        """
        Sends a prompt to OpenAI GPT and retrieves the response.

        Args:
            prompt (str): The prompt to send to GPT.

        Returns:
            str: GPT's response.
        """
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a Label Referee Agent."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1000,
        }
        max_tokens = 4096

        truncated_messages = truncate_chat_messages(data["messages"], max_tokens, data["model"])
        data["messages"] = truncated_messages
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            if response.status_code == 200:
                res_json = response.json()
                return res_json["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            return f"Error occurred: {str(e)}"

    def referee_labels(self, labels):
        """
        Referees five ranked labels to determine if they describe a unique Internet-connected device.

        Args:
            labels (list): A list of five dictionaries ranked by priority.

        Returns:
            dict or str: Unified label if consistent, or an error message if multiple devices are found.
        """
        if len(labels) != 5:
            raise ValueError("Invalid input. Please provide exactly five ranked labels.")

        # Convert input labels to a JSON string
        labels_json = json.dumps(labels, indent=4)
        
        # Define the GPT prompt
        prompt = f"""
            Given user input of five labels ranked by priority (higher rank = greater
            priority), referee if they describe a unique Internet-connected device.

            User Input:
            {labels_json}

        Output format:
          {{
              "vendor": "<vendor>",
              "type": "<type>",
              "product": "<product>"
          }}
        """

        # Send the prompt to OpenAI API
        gpt_response = self._send_request_to_gpt(prompt)

        # Parse and return the response
        try:
            return json.loads(gpt_response) if isinstance(gpt_response, str) and gpt_response.startswith("{") else gpt_response
        except json.JSONDecodeError:
            return gpt_response


# Example Usage
def label_referee_agent_run(input_labels, api_key):

    # Initialize the agent
    agent = LabelRefereeAgent(api_key)

    # # Input: Five ranked labels
    # input_labels = [
    #     {"vendor": "Netgear", "type": "Switch", "product": "GS324TP", "device description": "Smart Switch with 24 ports."},
    #     {"vendor": "Netgear", "type": "Switch", "product": "GS324TP", "device description": "24-port Smart Managed Switch."},
    #     {"vendor": "Netgear", "type": "Switch", "product": "GS324TP", "device description": "Suitable for SMB networks."},
    #     {"vendor": "Netgear", "type": "Switch", "product": "GS324TP", "device description": ""},
    #     {"vendor": "Netgear", "type": "Switch", "product": "", "device description": "Advanced VLAN support."}
    # ]

    # Referee the labels
    result = agent.referee_labels(input_labels)
    return result
