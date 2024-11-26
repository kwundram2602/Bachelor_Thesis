import labelbox as lb
import labelbox.types as lb_types
import uuid
import json


def read_data_row_ids(ndjson):
    """
    Reads Data Row IDs from ndjson file and returns them as a list.
    Useful for retrieving all data row ids of a project

    :param ndjson: Path to ndjson file
    """
    with open(ndjson, 'r', encoding='utf-8') as ndjson_file:
        ids=[]
        for line_number, line in enumerate(ndjson_file, start=1):
            # Parse die Zeile als JSON
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Fehler beim Parsen der Zeile {line_number}: {e}")
                continue
            data_row_id=json_data.get("data_row", {}).get("id")
            
            ids.append(data_row_id)
    print(ids)
    return ids
            
    
def set_global_key(data_row):
    """
    Sets global key for given data row.

    :param data_row: Data row object. Use data_row = get_data_row(<id>) before, to get data row by id.
    """
    global_key = str(uuid.uuid4())
    res = client.assign_global_keys_to_data_rows(
        [{
            "data_row_id": data_row.uid,
            "global_key": global_key
        }]
    )
    print(res)
# client init
client = lb.Client("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHZnanVhMncwcDN4MDcxZmRhdnJieHd4Iiwib3JnYW5pemF0aW9uSWQiOiJjbDN0dGpmd2IwN29jMDc1Yzhubno3YjV4IiwiYXBpS2V5SWQiOiJjbTNzb2dvMzUwMWU5MDd6cWRmNTExNzFkIiwic2VjcmV0IjoiMDRkNjdmODQ3YjExMzRjZDZkYjE2NWJjYWUzNzdkMGIiLCJpYXQiOjE3MzIyNzYwOTgsImV4cCI6MjM2MzQyODA5OH0.n4BU4BITKb84cennBDKZDXBcf2OhF6QcNWbLxyKQlHo")

dataset = client.get_dataset("cm3h8xqz9000b0758oacx744d")

# read data rows
data_row_ids= read_data_row_ids("D:\Bachelorarbeit\Export v2 project - zebrafish_ba_kjell - 11_22_2024.ndjson")

# set global key for every data row
for id in data_row_ids:
    # get data row by id
    data_row = client.get_data_row(id)
    # set global key
    set_global_key(data_row)