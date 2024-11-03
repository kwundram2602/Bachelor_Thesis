import os
import json
import argparse
import re

def ndjson_to_json(ndjson_file_path, output_directory):
    # Creates output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    with open(ndjson_file_path, 'r', encoding='utf-8') as ndjson_file:
        for line_number, line in enumerate(ndjson_file, start=1):
            # load line as json
            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Could not load JSON from line {line_number}:\n {e}")
                continue
            
            # extracts external id in json
            external_id = json_data.get("data_row", {}).get("external_id")
            if not external_id:
                print(f"line {line_number} has no external id.")
                continue
            # chunks of one video will be put in one folder
            pattern = r"(.*?)_combined"
            external_id_without_chunk=re.search(pattern, external_id).group(1)
            # Create folder 
            try:
                if not os.path.exists(os.path.join(output_directory,external_id_without_chunk)):
                    os.mkdir(os.path.join(output_directory,external_id_without_chunk))
                    print(f"Folder '{os.path.join(output_directory,external_id_without_chunk)}' created")
            except OSError as e:
                print(f"Could not create folder'{os.path.join(output_directory,external_id_without_chunk)}':\n {e}")
                
            # JSON file path with external_id
            json_file_path = os.path.join(output_directory,external_id_without_chunk,f"{external_id}.json")
            
            # Write JSON to file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            
            print(f"line {line_number} succesfully written to {json_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Conert NDJSON to JSON.')
    parser.add_argument('--ndjson_file_path', type=str, required=True, help='NDJSON file path')
    parser.add_argument('--output_directory', type=str, required=True, help='Output directory for JSON(s)')

    args = parser.parse_args()

    ndjson_to_json(args.ndjson_file_path, args.output_directory)
