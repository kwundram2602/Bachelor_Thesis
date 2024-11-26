import cv2
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np

def count_detections(labels_folder,image_path,output_path):
    
    
    for labeltxt in sorted(os.listdir(labels_folder)):
        print("labeltxt",labeltxt)
        img = cv2.imread(image_path)
        dh, dw, _ = img.shape
        print("img.shape",img.shape)
        print("dh, dw, _", dh, dw, _)
        with open(os.path.join(labels_folder, labeltxt), 'r') as file:
            data=file.readlines()
        file.close()
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
            #cv2.circle(img, (l,t), radius=0, color=(0, 0, 255), thickness=-1)
            #cv2.circle(img, (r,t), radius=0, color=(0, 0, 255), thickness=-1)
            #cv2.circle(img, (r,b), radius=0, color=(0, 0, 255), thickness=-1)
            #cv2.circle(img, (l,b), radius=0, color=(0, 0, 255), thickness=-1)

        rn= np.random.randint(0,256,256)
        cmap= np.array(rn)
        u8 = cmap.astype(np.uint8)
        print(u8)
        cv2.applyColorMap(img , u8 , 2)
        cv2.imwrite(os.path.join(output_path,"heatmap2.png"), img)
        break
        

# sbatch /home/k/kwundram/bcth/Bachelor_Thesis/Bashfiles/detections_count.sh
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--labels_folder', type=str, required=True, help='path to label txts')
    parser.add_argument('--image_path', type=str, required=True, help='path to example image to get shape ')
    parser.add_argument('--output_path', type=str, required=True, help='path to label txts')

    args = parser.parse_args()
    labels_folder =args.labels_folder
    image_path = args.image_path
    output_path=args.output_path
    count_detections(labels_folder,image_path,output_path)

