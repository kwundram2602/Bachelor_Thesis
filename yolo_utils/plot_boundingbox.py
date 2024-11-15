import cv2
import matplotlib.pyplot as plt
import argparse


def plot_bbox_to_image(image_path,label_path):
    
    img = cv2.imread(image_path)
    dh, dw, _ = img.shape

    fl = open(label_path, 'r')
    data = fl.readlines()
    fl.close()

    for dt in data:

        # Split string to float
        _, x, y, w, h = map(float, dt.split(' '))

        l = int((x - w / 2) * dw)
        r = int((x + w / 2) * dw)
        t = int((y - h / 2) * dh)
        b = int((y + h / 2) * dh)
        
        if l < 0:
            l = 0
        if r > dw - 1:
            r = dw - 1
        if t < 0:
            t = 0
        if b > dh - 1:
            b = dh - 1

        cv2.rectangle(img, (l, t), (r, b), (0, 0, 255), 1)

    plt.imshow(img)
    plt.show()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--image_path', type=str, required=True, help='Image path.  e.g /abc/123.png ')
    parser.add_argument('--label_path', type=str, required=True, help='Label text file path e.g /abc/123.txt')

    args = parser.parse_args()
    image_path =args.image_path
    label_txt = args.label_path
    plot_bbox_to_image(image_path,label_txt)