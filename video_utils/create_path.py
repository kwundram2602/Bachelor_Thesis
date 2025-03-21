import os 
import argparse

"""
helper function. can be used in bash scripts
"""
def create_path(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--path', type=str, required=True, help='path to create')
    
    # parse arguments
    args = parser.parse_args()
    
    dir= args.path
    create_path(dir)