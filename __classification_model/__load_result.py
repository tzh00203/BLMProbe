import sys
import re

# Add the project path for imports
# sys.path.append("")

# Configuration variables
CONFIG = {
    "paths": {
        "train_log_path": "./baseline",  # Baseline
        "mig_log_path": "./+ LLM-based Automatic Label Exploration",  # + LLM-based Automatic Label Exploration
        "binary_log_path": "./+ Protocol Association Based Label Migration",  # + Protocol Association Based Label Migration
        "none_log_path": "./Both Enhancements",  # Both Enhancements
    },
    "labels": [
        "Baseline",
        "+ LLM-based Automatic Label Exploration",
        "+ Protocol Association Based Label Migration",
        "Both Enhancements",
    ],
}

def load_train_result(config):
    """
    Generate the loss and accuracy from logs and visualize the results.

    :param config: Dictionary containing log paths and configuration details.
    """
    from __generate_util import (
        extract_val_metrics_and_epoch,
        plot_training_loss_and_acc,
    )

    # Load log files
    paths = config["paths"]
    logs = {
        "Baseline": open(paths["train_log_path"], "r", encoding="utf-8").readlines(),
        "+ LLM-based Automatic Label Exploration": open(paths["mig_log_path"], "r", encoding="utf-8").readlines(),
        "+ Protocol Association Based Label Migration": open(paths["binary_log_path"], "r", encoding="utf-8").readlines(),
        "Both Enhancements": open(paths["none_log_path"], "r", encoding="utf-8").readlines(),
    }

    # Extract loss and accuracy metrics
    records = {label: extract_val_metrics_and_epoch(lines) for label, lines in logs.items()}

    # Plot training loss and accuracy
    plot_training_loss_and_acc(
        records["Baseline"],
        records["+ LLM-based Automatic Label Exploration"],
        records["+ Protocol Association Based Label Migration"],
        records["Both Enhancements"],
        labels=config["labels"],
    )

    # Helper function to print the best validation accuracy
    def print_best_acc(log_name, log_lines):
        best_acc = 0
        for line in log_lines:
            if line.startswith("Iter:"):
                val_acc_pattern = r"Val Acc:\s*([0-9.]+)%"
                match = re.search(val_acc_pattern, line)
                if match:
                    acc = float(match.group(1))
                    if acc > best_acc:
                        best_acc = acc
        print(f"Best Validation Accuracy ({log_name}): {best_acc}%")

    # Print best validation accuracy for each log
    for label, lines in logs.items():
        print_best_acc(label, lines)


if __name__ == "__main__":
    load_train_result(CONFIG)
