import sys, os, json, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from __bing_exploring_agent import BingExploringAgent
from __label_referee_agent import LabelRefereeAgent
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json
from tqdm import tqdm
output_path = global_path.__agent_labels_path__
result_path = global_path.__crawler_search_result_path__

class AgentLabelingWorkflow:
    def __init__(self, explore_mode="gpt", referee_mode="gpt"):
        """
        Initialize the workflow with configurations for both agents.
        """
        self.bing_agent = BingExploringAgent(explore_mode)
        self.referee_agent = LabelRefereeAgent(referee_mode)
        self.referee_output = f"{output_path}_referee_{referee_mode}.json"
        self.record_output = f"{output_path}_record_{explore_mode}_{referee_mode}.json"    
        """
        Run the workflow where:
        1. Bing Exploring Agent processes data and extracts initial labels.
        2. Label Referee Agent evaluates and synthesizes the labels.

        Returns:
            dict: Final evaluated labels from the Label Referee Agent.
        """
    def run_agent_1(self):
        # Step 1: Bing Exploring Agent Processes the URIs
        print("[Workflow] Starting Bing Exploring Agent...")
        self.bing_agent.run()  # Bing Exploring Agent extracts initial labels
        print("[Workflow] Bing Exploring Agent completed.")
    def run_agent_2(self):
        dir_path = f"{result_path}webpage_log/"
        bing_results = {}
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                with open(dir_path + filename, "r", encoding='utf-8') as json_file:
                    local_results = json.load(fp=json_file)
                    bing_results.update(local_results)
        print("[Workflow] Processing results with Label Referee Agent...")
        # Step 2: Label Referee Agent Refines Results
        record_labels = {}
        final_labels = {}
   
   
        for line, sanitization_entries in tqdm(bing_results.items(), desc="Processing lines"):
            # Extract labels and device descriptions for each line
            labels = [entry["openai_labels"] for entry in sanitization_entries]
            # descriptions = [entry.get("web_info", "") for entry in sanitization_entries]

            # Use Label Referee Agent to evaluate the consistency and relevance of labels
            referee_label_tmp = self.referee_agent.referee_labels(labels)
            final_labels[line] = referee_label_tmp
            record_labels[line] = {"explore_labels": labels, "referee_label": referee_label_tmp}
            

        print("[Workflow] Label Referee Agent completed.")
        return final_labels, record_labels
    def run_agent_3(self, final_output):
        # Output Final Labels
        print("\n[Workflow] Final Evaluated Labels:")
        final_output_referee, final_output_record = final_output[0], final_output[1]
        for line, label in final_output_referee.items():
            print(f"Line {line}: {label}")
        save_dict_to_json(self.referee_output, final_output_referee)
        save_dict_to_json(self.record_output, final_output_record)

        
    def run_agent(self):
        self.run_agent_1()
        self.run_agent_3(self.run_agent_2())


if __name__ == "__main__":
    agent_runner = AgentLabelingWorkflow(explore_mode="gpt", referee_mode="gpt")
    agent_runner.run_agent()