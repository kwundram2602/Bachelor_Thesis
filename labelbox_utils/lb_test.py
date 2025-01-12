from bcth.Bachelor_Thesis.labelbox_utils.lb_label_upload import get_datarow_id_by_external_id,read_labels,initialize_lbbx_client,get_global_key_by_external_id,create_image_bbox_anno,upload_labels_job
from lbox.exceptions import ResourceNotFoundError,LabelboxError
import logging
import labelbox.data.annotation_types as lb_types

#B1D1_C1_ST_c22671.png

logging.basicConfig(level = logging.INFO,format='%(asctime)s - %(levelname)s: %(message)s',datefmt='%H:%M:%S')

# client init
client = initialize_lbbx_client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")
label_path=args.label_path
ndjson_path= args.ndjson_path
#label_path =r"D:\Bachelorarbeit\test_labels"
# read labels from folder and return dict
labels_from_txt = read_labels(label_path,1024,1280)


for external_id in labels_from_txt:
    print(external_id)
    label = []
    annotation_list=[]
    
    global_key = get_global_key_by_external_id(ndjson_path,external_id)
    #did=get_datarow_id_by_external_id(ndjson_path,external_id)
    #print(did)
    if global_key is None:
        logging.error(f"Could not get global key for {external_id}")
        continue
    
    logging.info(f" Global Key {global_key}")
    try:
        for bbox in labels_from_txt[external_id]:
            anno=create_image_bbox_anno("zebrafish",bbox["top"],bbox["left"],bbox["height"],bbox["width"])
            annotation_list.append(anno)
    except Exception as e:
        logging.error(e)
        continue
    
    if len(annotation_list) > 0:
        label.append(
        lb_types.Label(data={"global_key" : global_key
                            },
                    annotations=annotation_list))
        print("label",label)
    else:
        logging.info(f"No annotations for {external_id}")
        continue
    try:
        upload_labels_job(label,client,"cm3zzwwe5013507xg40mg2ubu")
    except LabelboxError as e:
        logging.error(e)