import cv2 as cv
import os
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_folder', type=str, required=True, help='path to folder with videos')
        
    # parse arguments
    args = parser.parse_args()

    warm_up_data = args.data_folder #r"/scratch/tmp/kwundram/bcth/data/warmup_data"

