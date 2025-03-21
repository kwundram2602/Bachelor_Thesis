import matplotlib.pyplot as plt
import pandas as pd
import logging

import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
import argparse
"""
plot yolo results. (map, precision, recall)
"""
# Function to parse the text file and extract relevant data
def parse_file(file_path):
    # Read the file into a pandas DataFrame
    df = pd.read_csv(file_path, sep=r"\s+", header=None, engine="python")

    # Manuell Spaltennamen zuweisen
    column_names = [
        "Epochs", "gpu_mem", "box", "obj", "cls", "total", 
        "labels", "img_size", "prec", "recall", 
        "mAP.5", "mAP.5:.95", "val_box", "val_obj", "val_cls"
    ]
    if len(df.columns) != len(column_names):
        raise ValueError(f"Die Datei hat {len(df.columns)} Spalten, aber {len(column_names)} Namen wurden angegeben.")

    df.columns = column_names
    return df

# Function to plot precision and recall
def plot_precision_recall(df,save_dir):
    epochs = df['Epochs']
    precision = df['prec']
    recall = df['recall']

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, precision, label='Precision', linestyle='-', marker='o', markersize=4, linewidth=2, color='#0072B2', alpha=0.8)
    plt.plot(epochs, recall, label='Recall', linestyle='--', marker='s', markersize=4, linewidth=2, color='#E69F00', alpha=0.8)
# Annotate values every 10 epochs
    for i in range(0, len(epochs), 10):
        plt.annotate(f"{precision[i]:.3f}", (epochs[i], precision[i]), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, color='black')
        plt.annotate(f"{recall[i]:.3f}", (epochs[i], recall[i]), textcoords="offset points", xytext=(0, -10), ha='center', fontsize=8, color='black')

    plt.xticks(ticks=range(0, len(epochs), 10), labels=epochs[::10])
    plt.xlabel('Epochs')
    plt.ylabel('Metrics')
    plt.title('Precision and Recall Over Epochs')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    save_path=os.path.join(save_dir,"precision_recall.png")
    plt.imsave(save_path)
    #plt.show()

# Function to plot mAP values
def plot_map_values(df,save_dir):
    epochs = df['Epochs']
    map_5 = df['mAP.5']
    map_5_95 = df['mAP.5:.95']

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, map_5, label='mAP@.5', linestyle='-', marker='^', markersize=4, linewidth=2, color='#56B4E9', alpha=0.8)
    plt.plot(epochs, map_5_95, label='mAP@.5:.95', linestyle='--', marker='d', markersize=4, linewidth=2, color='#D55E00', alpha=0.8)
# Annotate values every 10 epochs
    for i in range(0, len(epochs), 10):
        plt.annotate(f"{map_5[i]:.3f}", (epochs[i], map_5[i]), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, color='black')
        plt.annotate(f"{map_5_95[i]:.3f}", (epochs[i], map_5_95[i]), textcoords="offset points", xytext=(0, -10), ha='center', fontsize=8, color='black')

    plt.xticks(ticks=range(0, len(epochs), 10), labels=epochs[::10])
    plt.xlabel('Epochs')
    plt.ylabel('mAP Metrics')
    plt.title('mAP Metrics Over Epochs')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # save dir map values
    save_path=os.path.join(save_dir,"mAP_metrics.png")
    plt.imsave(save_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--file_path", required=True, help="Path to the results.txt file")
    args = argparser.parse_args()
    file_path = args.file_path
    logging.info(f"Using file: {file_path}")

    try:
        # Parse the file
        data = parse_file(file_path)
        print(data)
        file_dir=os.path.dirname(file_path)
        # Plot precision and recall
        plot_precision_recall(data,file_dir)

        # Plot mAP values
        plot_map_values(data,file_dir)

    except Exception as e:
        print(f"Error: {e}")
