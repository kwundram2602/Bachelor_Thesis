import os
import shutil

def get_files_in_directory(directory):
    files_in_directory = set()
    for root, _, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            files_in_directory.add(relative_path)
    return files_in_directory

def find_unique_files(folder_a, folder_b):
    files_in_a = get_files_in_directory(folder_a)
    files_in_b = get_files_in_directory(folder_b)
    
    unique_files = files_in_a - files_in_b
    return unique_files

    
def copy_txt_files(src, dst):
    for root, dirs, files in os.walk(src):
        print(f"root: {root}")
        for file in files:
            if file.endswith('.txt'):
                src_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, src)
                dst_dir = os.path.join(dst, relative_path)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src_file, dst_dir)
                print(f"Copied {src_file} to {dst_dir}")

if __name__ == "__main__":
    src_folder = "/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels"
    dst_folder = "/scratch/tmp/kwundram/bcth/data/whole_data/converted/labels_rescaled"
    #copy_txt_files(src_folder, dst_folder)
       
    unique_files = find_unique_files(src_folder, dst_folder)
    
    print("Files in folder_a but not in folder_b:")
    for file in unique_files:
        print(file)