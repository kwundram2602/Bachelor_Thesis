import os
from sklearn.model_selection import train_test_split
import argparse

def list_absolute_paths(folder_path,output_path,file_pattern):
    """
    Lists all absolute paths of all files matching a specific file pattern and writes them to a text file.

    :param folder_path: folder with all files
    :param output_path: path where text file will be written to
    :param file_pattern: file pattern. (e.g *.png or *.mp4)
    """ 
    paths = []
    for filename in os.listdir(folder_path):
        if filename.endswith(file_pattern):
        # Join folder path and filename to get absolute path
            absolute_path = os.path.join(folder_path, filename)
            paths.append(absolute_path)

    # Open the output file in write mode
    with open(output_path, "a") as f:
        # Write each path to the file, followed by a newline
        f.write("\n".join(paths))
        f.write("\n")
    
def video_data_split(video_folder,output_path):
    mp4_paths=[]
    for filename in os.listdir(video_folder):
        if filename.endswith(".mp4"):
            absolute_path = os.path.join(video_folder, filename)
            mp4_paths.append(absolute_path)
    train_set,val_set = train_test_split(mp4_paths, test_size=0.3, random_state=42)
    val_set,test_set = train_test_split(mp4_paths, test_size=0.5, random_state=42)
    print("train_set:",train_set,"\n")
    print("val_set:",val_set,"\n")
    print("test_set:",test_set,"\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--folder_path', type=str, required=True, help='path to folder')
    parser.add_argument('--output_path', type=str, required=True, help='output_path')
    parser.add_argument('--file_pattern', type=str, required=False, help='file_pattern')

    # parse arguments
    args = parser.parse_args()
    video_data_split2(args.folder_path,args.output_path)