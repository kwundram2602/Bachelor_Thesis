from lb_data_row_upload_chunkwise import check_if_id_exists,load_ndjson
from lb_label_upload import get_datarow_id_by_external_id
import labelbox as lb
import labelbox.types as lb_types
from lbox.exceptions import ResourceNotFoundError,LabelboxError
import uuid
from PIL import Image
import requests
import base64
import argparse
import os
import itertools
import logging

# script for deleting duplicates in labelbox
def find_duplicates(data):
    external_ids = [entry["data_row"]["external_id"] for entry in data]
    duplicates = set([x for x in external_ids if external_ids.count(x) > 1])
    return duplicates

def delete_duplicates_by_ndjson(client,ndjson):
    """
    Finds external_ids that appear more than once in ndjson
    and deletes these rows by data row id without using dataset.data_rows_for_external_id()
    """
    data= load_ndjson(ndjson)
    duplicates=find_duplicates(data)
    logging.info(f" Duplicates: {duplicates}")
    for external_id in duplicates:
        try:
            row_id=get_datarow_id_by_external_id(ndjson,external_id)
            data_row = client.get_data_row(row_id)
            logging.info(f"data_rows{data_row}")
            #data_row.delete()
        except LabelboxError as e:
            logging.error(e)
    
    
def delete_duplicates(data,dataset):
    external_ids = [entry["data_row"]["external_id"] for entry in data]
    for ex_id in external_ids:
        row_list = dataset.data_rows_for_external_id(ex_id, limit=20)
        if len(row_list) > 1:
            print(len(row_list))
            # delete rows except one
            deletion_count = len(row_list) - 1
            logging.INFO(f"Delete {deletion_count} rows")
            # get rows to delete
            rows_to_delete=list(itertools.islice(row_list,deletion_count))
            for row in rows_to_delete:
                logging.INFO(row)
                #row.delete()
                
        
# dataset and client
client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")
logging.basicConfig(level = logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s',datefmt='%H:%M:%S')
 
# ndjson. current data
ndjson="/scratch/tmp/kwundram/bcth/data/whole_data/export_5_12_24.ndjson"

#delete_duplicates(data,dataset)
delete_duplicates_by_ndjson(client,ndjson)