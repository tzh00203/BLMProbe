import json
from __agent_utils import LLMCaller

class LabelRefereeAgent:
    """
    A Label Referee Agent for evaluating and synthesizing Internet-connected device labels.
    It leverages gpt to referee five ranked labels and determine if they describe a unique device.
    """

    def __init__(self, mode="gpt"):
        # Send the prompt to LLM API
        self.caller = LLMCaller(mode=mode)

    def referee_labels(self, labels):
        """
        Referees five ranked labels to determine if they describe a unique Internet-connected device.

        Args:
            labels (list): A list of five dictionaries ranked by priority.

        Returns:
            dict or str: Unified label if consistent, or an error message if multiple devices are found.
        """
        if len(labels) > 5:
            raise ValueError("Invalid input. Please provide exactly five ranked labels.")

        # Convert input labels to a JSON string
        labels_json = json.dumps(labels, indent=4)
        
        # Define the gpt prompt
        system_prompt = """
                You are a label referee agent, and the user will enter the asset labels of network devices extracted from five web pages, 
                each label conforms to the json format and contains four attributes: vendor, type, product, device_description. 
                These pages originate from a single call to a search engine query, and you need to referee network device is relevant 
                for this query based on the labels extracted from the five web pages. 
                The output information contains three dimensions: device vendor name(vendor), device type(type), device model information(product)
        
                    User input: dictionary type {uri, title, web_info}
                    Your answer output format:
                    {'vendor': '', 'type': '', 'product': ''}
                    Attention:
                    1. Based on the five labels referee this web search query most likely describes network device asset information
                    2. If the vendor or device type is unknown, the attribute value is "null".
                    3. The attribute value of the referee must come from the attribute value in the tag information ({vendor, type, product}) entered by the user
                    4. If the input information does not contain network device information, the attribute value corresponding to each attribute in the dictionary is null. (The vendor and type are irrelevant to the network device.)
                    5. The more advanced the label entered by the user indicates a higher level of trustworthiness
                    6. Your answer only needs to be given a dictionary of results and does not need to contain additional strings

        """
        
        referee_agent_prompt = """
        You are an IoT Device Label Referee Agent. Specialized in resolving network-connected device labels for IoT ecosystems. The user will input a search query and multiple candidate labels extracted 
        from webpages related to the query. Each label corresponds to a webpage and contains attributes (vendor, type, product). 
        Your task is to determine the **unique final label** that best represents the query based on consensus and contextual relevance.  

        **Input Format**:  
        {  
        "query": "[SEARCH_QUERY_KEYWORDS]",  
        "labels": [  
            {"vendor": "...", "type": "...", "product": "..."},  
            ...  
        ]  
        }  

        **Output Format**:  
        {  
        "vendor": "[FINAL_VENDOR]",  
        "type": "[FINAL_DEVICE_TYPE]",  
        "product": "[FINAL_PRODUCT]"  
        }  

        **Attention**:  
        1. **Source Constraints**:  
        - The final label's attributes MUST originate from the input `labels` list. Do NOT invent new values.  
        2. **Uniqueness Logic**:  
        - **Vendor & Type Consensus**: Prioritize the vendor-type pair with the highest frequency across `labels`.  
        - **Query Relevance**: If the `query` explicitly mentions a vendor/type (e.g., "Cisco routers"), override consensus to match the query’s intent.  
        - **Product Ambiguity**: If multiple conflicting products exist for the chosen vendor-type pair, leave `product` as "null".  
        3. **Fallback Rules**:  
        - If no vendor-type pair has clear consensus (e.g., ties or irrelevance to the query), output all attributes as "null".  
        - If all labels have invalid vendor/type (e.g., "null"), output all attributes as "null".  
        4. **Output Formatting**:  
        - Return **only** the final dictionary. Do NOT include explanations or metadata.  
        5. The sequential priority weights of the input labels are listed in descending order.
        6. Prioritize potential IoT device keywords in query statements

        """

        message= [
            {"role": "system", "content": referee_agent_prompt},
            {"role": "user", "content": f"user input: {labels_json}"},
        ]
        llm_response = self.caller._send_request_to_llm_DMXapi(message=message)
        print(llm_response)
        # Parse and return the response
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError as e:
            return f"Error occurred: {e}"


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
