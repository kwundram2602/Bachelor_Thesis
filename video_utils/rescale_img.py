import os
from PIL import Image
import argparse

def rescale_images(input_folder, output_folder, target_resolution):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            img = img.resize(target_resolution, Image.LANCZOS)
            output_path = os.path.join(output_folder, filename)
            img.save(output_path)
            print(f"Rescaled {filename} and saved to {output_path}")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input_folder", required=True, type=str)
    argparser.add_argument("--output_folder", required=True, type=str)
    argparser.add_argument("--width", required=True, type=int)
    argparser.add_argument("--height", required=True, type=int)
    args = argparser.parse_args()
    
    input_folder = args.input_folder
    output_folder = args.output_folder
    target_resolution = (args.width, args.height)

    for folder in os.listdir(input_folder):
        if not os.path.isdir(os.path.join(input_folder, folder)):
            print(os.path.join(input_folder, folder), "is not a folder. Skipping...")
            continue
        else:
            rescale_images(os.path.join(input_folder, folder), os.path.join(output_folder, folder), target_resolution)
    