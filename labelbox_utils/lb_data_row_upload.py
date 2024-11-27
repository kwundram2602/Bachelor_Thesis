import labelbox as lb
import labelbox.types as lb_types
import uuid
from PIL import Image
import requests
import base64
import argparse
import os


def upload_image(file_path,client,dataset,external_id):
    # upload the file to Labelbox storage  
    file_url = client.upload_file(file_path)
    global_key = str(uuid.uuid4())
    # create the data row with a global key
    task = dataset.create_data_rows([{
    "row_data": file_url,
    "global_key": global_key,
    "external_id":external_id
    }])
    print(f"Processing {file_path} ...\n")
    task.wait_till_done()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot bounding box to image.')
    parser.add_argument('--images_folder', type=str, required=True, help='images folder path')
    
    args = parser.parse_args()
    images_folder=args.images_folder
    # client init
    client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
    dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")
    
    for image in os.listdir(images_folder):
        image_path=os.path.join(images_folder,image)
        print(image_path)
        upload_image(image_path,client,dataset,image)