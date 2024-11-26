import os
import argparse
# functions to change labels in txt files.

def delete_classes(labels_folder:str,class_index:int):
    """
    Deletes all classes from label text files besides a specific class.
    Function overwrites exiting text files.

    :param labels_folder: folder with all label text files.
    :param class_index: this class will be kept in the result label text file
    """
    print(f"Deleting all instances with other class index than {class_index}")
    for labeltxt in os.listdir(labels_folder):
        print(f"label file:{labeltxt}")
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            lines = [line for line in file if line.strip().startswith(class_index)]
            print(f"lines in {file} \n", lines)
            file.close()
            
        with open(os.path.join(labels_folder, labeltxt), 'w') as file:  
            file.writelines(lines)
            print("written...")
            file.close()
            
            
def change_classID(labels_folder:str,old_index:int,new_index:int):
    """
    Changes old class ID to new class ID.

    :param labels_folder: folder with all label text files.
    :param old_index: this index will be replaced
    :param new_index: this is the new index
    """
    print(f"Change {old_index} ID to {new_index} ID")
    for labeltxt in os.listdir(labels_folder):
        modified_lines = []
        print(f"label file:{labeltxt}")
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            for line in file:
                print(f"line in file: {line} ")
                if line.startswith(str(old_index) + " "):
                    # replace old index with new index
                    modified_line = line.replace(str(old_index), str(new_index), 1)
                    print(f"modified line: {modified_line} ")
                    modified_lines.append(modified_line)
                else:
                    print("Line does not begin with old index! \n")
                    # line does not begin with old index, so old line will be used
                    modified_lines.append(line)
            file.close()
        with open(os.path.join(labels_folder, labeltxt), 'w') as file:
            print("modified_lines",modified_lines)  
            file.writelines(modified_lines)
            print("written...")
            file.close()
                      
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--labels_folder', type=str, required=True, help='path to folder')
    parser.add_argument('--class_index', type=str, required=False, help='class index. For Deleting')
    parser.add_argument('--old_index', type=str, required=False, help='old index. For changing ID')
    parser.add_argument('--new_index', type=str, required=False, help='new index. For changing ID')
    # parse arguments
    args = parser.parse_args()
    
    labels_folder = args.labels_folder
    class_index= args.class_index
    #delete_classes(labels_folder,"14")
    change_classID(labels_folder,1,0)