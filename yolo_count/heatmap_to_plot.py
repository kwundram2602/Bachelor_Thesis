import cv2
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
def count_detections(labels_folder,image_path,output_path,mean_factor,image_width,image_height):
    
    # Get the current date and time
    now = datetime.now()
    formatted_date = now.strftime("%H.%M.%S")  
    print("Formatted date:", formatted_date)
    
    masc = np.zeros((image_height,image_width),dtype = np.float32)
    # for all label txt files
    for labeltxt in sorted(os.listdir(labels_folder)):
        print("labeltxt",labeltxt)
        #img = cv2.imread(image_path,cv2.IMREAD_GRAYSCALE)
        img = cv2.imread(image_path)
        dh, dw, _= img.shape
        print("img.shape",img.shape)
        print("dh, dw, _", dh, dw, _)
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            data=file.readlines()
        # for line in text file
        for dt in data:

            # Split string to float
            #normalized center coordinates, w and h are the normalized width
            # and height of the bounding box
            _, x, y, w, h = map(float, dt.split(' '))
            # convert to pixel coordinates
            # left, right, top, bottom
            l = int((x - w / 2) * dw)
            r = int((x + w / 2) * dw)
            t = int((y - h / 2) * dh)
            b = int((y + h / 2) * dh)
            
            #ensure the bounding box coordinates do not exceed the image dimensions
            if l < 0:
                l = 0
            if r > dw - 1:
                r = dw - 1
            if t < 0:
                t = 0
            if b > dh - 1:
                b = dh - 1
            
            print("l",l)
            print("r",r)
            print("t",t)
            print("b",b)
            
            masc[t:b,l:r]+=1
            # next line
        #next label file
        
    #masc_u8=(masc/256).astype(np.uint8)
    print("np.max(masc)",np.max(masc))
    print("np.median(masc)",np.median(masc))
    print("np.mean(masc)",np.mean(masc))
    image_mean= np.mean(img)
    cmap_n=2
    
    # normalize masc with maximum 
    masc_u8 = ((masc / np.max(masc)) * 256).astype(np.uint8)
    
    
    # create plot
    dpi=100
    fig_width = image_width / dpi
    fig_height = image_height / dpi
    fig, ax = plt.subplots(figsize=(fig_width, fig_height),dpi=dpi)
    # plot color Map
    c = ax.imshow(masc_u8, cmap='viridis', origin='upper', extent=[0, image_width, 0, image_height])
    # Add a color bar
    plt.colorbar(c, ax=ax, label='Intensity')
    #ax.axis('off')  # Turn off axis labels and ticks
    ax.set_xlim(0, image_width)
    ax.set_ylim(0, image_height)
    # Save the plot as an image
    output_file=os.path.join(output_path,"heatmap_plot_new_u8.png")
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight',pad_inches=0)
    
    
        
        
        

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/detections_count.sh
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--labels_folder', type=str, required=True, help='path to label txts')
    parser.add_argument('--image_path', type=str, required=True, help='path to example image to get shape ')
    parser.add_argument('--output_path', type=str, required=True, help='path to label txts')
    parser.add_argument('--image_height', type=str, required=False, help='image_height')
    parser.add_argument('--image_width', type=str, required=False, help='image_width')

    args = parser.parse_args()
    labels_folder =args.labels_folder
    image_path = args.image_path
    output_path=args.output_path
    image_height=1024
    image_width=1280

    count_detections(labels_folder,image_path,output_path,0.025,image_width,image_height)

