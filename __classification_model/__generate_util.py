import sys
import time
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline


def loading_animation(message):
    """
    Display a loading animation in the terminal.

    Args:
        message (str): The message to display alongside the animation.
    """
    animation = ["|", "/", "-", "\\"]
    idx = 0

    while True:
        sys.stdout.write(f"\r{message} {animation[idx % len(animation)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)


def extract_val_metrics_and_epoch(lines):
    """
    Extract validation metrics (Loss and Accuracy) and corresponding epoch from log lines.

    Args:
        lines (list): A list of log lines.

    Returns:
        list: A list of [epoch, val_loss, val_acc].
    """
    epoch_loss_acc_record = []
    current_epoch = -1

    for i, line in enumerate(lines):
        match = re.search(r'Val\s*Loss\s*([0-9.]+)\s*,\s*Val\s*Acc\s*:?\s*([0-9.]+)%', line)
        if match:
            val_loss = float(match.group(1))
            val_acc = float(match.group(2))

            if i + 1 < len(lines):
                next_line = lines[i + 1]
                epoch_match = re.search(r'Epoch:(\d+)/(\d+)', next_line)
                if epoch_match:
                    current_epoch_tmp = int(epoch_match.group(1))
                    if current_epoch_tmp > current_epoch:
                        current_epoch = current_epoch_tmp
                        epoch_loss_acc_record.append([current_epoch, val_loss, val_acc])

    return epoch_loss_acc_record


def plot_training_loss_and_acc(record1, record2, record3, record4, labels, output_dir='./fig'):
    """
    Plot training loss and accuracy comparisons for multiple records.

    Args:
        record1, record2, record3, record4 (list): Training records [epoch, loss, acc].
        labels (list): Labels for each record, used in the legend.
        output_dir (str): Directory to save the output figures.
    """
    def smooth_plot(x, y, label, linestyle):
        x_smooth = np.linspace(min(x), max(x), 300)
        spline = make_interp_spline(x, y)
        y_smooth = spline(x_smooth)
        plt.plot(x_smooth, y_smooth, label=label, linestyle=linestyle)

    fig_width, fig_height = 12 / 2.54, 6 / 2.54  # Figure size in inches

    # Extract epochs, losses, and accuracies
    def extract_metrics(record):
        return [i[0] for i in record], [i[1] for i in record], [i[2] for i in record]

    epochs1, losses1, accs1 = extract_metrics(record1)
    epochs2, losses2, accs2 = extract_metrics(record2)
    epochs3, losses3, accs3 = extract_metrics(record3)
    epochs4, losses4, accs4 = extract_metrics(record4)

    # Plot Loss curves
    plt.figure(figsize=(fig_width, fig_height))
    smooth_plot(epochs1, losses1, f'{labels[0]} Loss', linestyle='-')
    smooth_plot(epochs2, losses2, f'{labels[1]} Loss', linestyle='--')
    smooth_plot(epochs3, losses3, f'{labels[2]} Loss', linestyle='-.')
    smooth_plot(epochs4, losses4, f'{labels[3]} Loss', linestyle=':')
    plt.xlabel('Epoch', fontweight='bold')
    plt.ylabel('Loss', fontweight='bold')
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/training_loss_comparison.pdf', format='pdf', bbox_inches='tight')
    plt.close()

    # Plot Accuracy curves
    plt.figure(figsize=(fig_width, fig_height))
    smooth_plot(epochs1, accs1, f'{labels[0]} Accuracy', linestyle='-')
    smooth_plot(epochs2, accs2, f'{labels[1]} Accuracy', linestyle='--')
    smooth_plot(epochs3, accs3, f'{labels[2]} Accuracy', linestyle='-.')
    smooth_plot(epochs4, accs4, f'{labels[3]} Accuracy', linestyle=':')
    plt.xlabel('Epoch', fontweight='bold')
    plt.ylabel('Accuracy', fontweight='bold')
    plt.legend(fontweight='bold')
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/training_acc_comparison.pdf', format='pdf', bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    test_log_line = "Iter: 3180,Train Loss 1.5,Train Acc 0.75,Val Loss 1.99,Val Acc:81.46%,Time:1:01:03"
    match = re.search(r'Val Loss ([0-9.]+),Val Acc:([0-9.]+)%', test_log_line)
    if match:
        print(f"Val Loss: {match.group(1)}, Val Acc: {match.group(2)}")
