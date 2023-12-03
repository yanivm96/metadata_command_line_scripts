import argparse
import airr
import json
import csv
import ast

from airr import load_rearrangement, dump_rearrangement, validate_rearrangement, validate_airr, read_airr

METADATA_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\PRJNA248411\project_metadata\metadata.json'
BIOSAMPLE_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\PRJNA248411\tsv_metadata\biosample.tsv'
SRA_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\PRJNA248411\tsv_metadata\sra.tsv'
PROJECT_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\PRJNA248411\tsv_metadata\project.tsv'


BIOSAMPLE_JSON_FORMAT_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\AIRR_BioSample_v1.0.json'
SRA_JSON_FORMAT_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\AIRR_SRA_v1.0.json'
PROJECT_JSON_FORMAT_PATH = r'C:\Users\yaniv\Desktop\work\command_line_Scripts\PROJECT.json'




def convert_tsv_to_json():
    data = {'Repertoire': []}
    counter = 0
    rep_list = []
    biosample_reader = airr.read_rearrangement(BIOSAMPLE_PATH)
    sra_reader = airr.read_rearrangement(SRA_PATH)
    project_reader = airr.read_rearrangement(PROJECT_PATH)

    for row in biosample_reader:
        try:
            repertoire = airr.schema.RepertoireSchema.template()
            update_repertoire(row, repertoire, BIOSAMPLE_JSON_FORMAT_PATH)
            rep_list.append(repertoire)
        except Exception as e:
            print(f"Error processing biosample_reader row: {e}")

    # Loop for sra_reader
    for row in sra_reader:
        try:
            update_repertoire(row, rep_list[counter], SRA_JSON_FORMAT_PATH)
            counter += 1
        except Exception as e:
            print(f"Error processing sra_reader row: {e}")

    # Reset counter
    counter = 0

    # Loop for project_reader
    for row in project_reader:
        try:
            update_repertoire(row, rep_list[counter], PROJECT_JSON_FORMAT_PATH)
            data['Repertoire'].append(rep_list[counter])
            counter += 1
        except Exception as e:
            print(f"Error processing project_reader row: {e}")


    json_file_path = 'metadata.json'
    airr.write_airr(json_file_path, data)

def search_key(data, target_key, new_value):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                data[key] = new_value
                return True
            elif isinstance(value, (dict, list)):
                result = search_key(value, target_key, new_value)
                if result:
                    return True
    elif isinstance(data, list):
        for item in data:
            result = search_key(item, target_key, new_value)
            if result:
                return True
            
    return False

def extract_key(key):
    if '.' in key:
        if len(key.split('.')) == 3:
            return key.split('.')[2]
        
        return key.split('.')[1]

    return key

def repear_value(value):
    # Check if the value is a string and starts with '{' and ends with '}'
    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
        try:
            # Safely evaluate the string to convert it to a Python object
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # If there's an error in conversion, return the original value
            return value
    else:
        # Return the value as is if it does not match the pattern
        return value

def update_repertoire(row, repertoire, type):
    not_include = ["AIRR-seq", "", None]

    for key, value in row.items():
        new_key = translate_key(key, type)
        if  new_key not in not_include:
            new_key = extract_key(new_key)
            new_key = change_new_key_to_currect_name(new_key)
            value = repear_value(value)
            if not search_key(repertoire, new_key, value):
                repertoire[new_key] = value
    
    return repertoire


def change_new_key_to_currect_name(new_key):
    if new_key == "age":
        return "age_event"

    return new_key


def translate_key(current_key, type):
    with open(type, 'r') as json_format:
        format = json.load(json_format)
    
    for key, value in format.items():
        if key == current_key:
            return value
    
    return None



if __name__ == "__main__":
    convert_tsv_to_json()