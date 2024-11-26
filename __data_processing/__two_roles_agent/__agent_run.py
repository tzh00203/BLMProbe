from bing_exploring_agent import BingExploringAgent
from label_referee_agent import LabelRefereeAgent
import __agent_config
from __utils.__path_util import __agent_labels_path__

output_path = __agent_labels_path__

class AgentLabelingWorkflow:
    def __init__(self, bing_agent_config, referee_agent_config):
        """
        Initialize the workflow with configurations for both agents.

        Args:
            bing_agent_config (dict): Configuration for the Bing Exploring Agent.
            referee_agent_config (dict): Configuration for the Label Referee Agent.
        """
        self.bing_agent = BingExploringAgent(bing_agent_config)
        self.referee_agent = LabelRefereeAgent(referee_agent_config)

    def run_workflow(self):
        """
        Run the workflow where:
        1. Bing Exploring Agent processes data and extracts initial labels.
        2. Label Referee Agent evaluates and synthesizes the labels.

        Returns:
            dict: Final evaluated labels from the Label Referee Agent.
        """
        # Step 1: Bing Exploring Agent Processes the URIs
        print("[Workflow] Starting Bing Exploring Agent...")
        bing_results = self.bing_agent.run()  # Bing Exploring Agent extracts initial labels

        print("[Workflow] Bing Exploring Agent completed.")
        print("[Workflow] Processing results with Label Referee Agent...")

        # Step 2: Label Referee Agent Refines Results
        final_labels = {}
        for line, sanitization_entries in bing_results.items():
            # Extract labels and device descriptions for each line
            labels = [entry["openai_labels"] for entry in sanitization_entries]
            descriptions = [entry.get("web_info", "") for entry in sanitization_entries]

            # Use Label Referee Agent to evaluate the consistency and relevance of labels
            final_labels[line] = self.referee_agent.evaluate_labels(labels, descriptions)

        print("[Workflow] Label Referee Agent completed.")
        return final_labels


if __name__ == "__main__":
    # Configuration for Bing Exploring Agent
    API_KEY_1 = __agent_config.bing_exploring_agent_api_key
    API_KEY_2 = __agent_config.label_referee_agent_api_key
    # Initialize Workflow
    workflow = AgentLabelingWorkflow(API_KEY_1, API_KEY_2)

    # Run the Workflow
    final_output = workflow.run_workflow()

    # Output Final Labels
    print("\n[Workflow] Final Evaluated Labels:")
    for line, label in final_output.items():
        print(f"Line {line}: {label}")
    from __utils.__save_file_util import save_dict_to_json
    save_dict_to_json(__agent_labels_path__, final_output)
