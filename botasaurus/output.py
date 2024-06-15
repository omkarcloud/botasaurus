from json import dumps
from .decorators_utils import create_output_directory_if_not_exists
from .utils import (
    read_file as _read_file,
    relative_path,
    write_json as _write_json,
    read_json as _read_json,
    write_html as _write_html,
    write_file as _write_file,
)
from .beep_utils import prompt
import os

def is_slash_not_in_filename(filename):
    return "/" not in filename and "\\" not in filename


def append_output_if_needed(filename):
    create_output_directory_if_not_exists()
    filename = str(filename).strip()
    if is_slash_not_in_filename(filename):
        return "output/" + filename
    return filename


def fix_json_filename(filename):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".json"):
        filename = filename + ".json"
    return filename


def read_json(filename):
    filename = fix_json_filename(filename)

    return _read_json(filename)



def write_temp_json(data, log=True):
    filename = "temp"

    try:

        filename = append_output_if_needed(filename)

        if not filename.endswith(".json"):
            filename = filename + ".json"

        _write_json(data, filename)

        if log:
            print(f"View written JSON file at {filename}")
    except PermissionError:
        prompt(
            f"{filename} is currently open in another application. Please close the the Application and press 'Enter' to save."
        )
        return write_json(data, filename, log)

    return filename
def read_temp_json():
    filename = fix_json_filename("temp")
    return _read_json(filename)


def file_exists(filename):
    filename = append_output_if_needed(filename)

    try:
        with open(filename, "r"):
            return True
    except FileNotFoundError:
        return False


def write_json(data, filename, log=True):
    # if type(data) is list and len(data) == 0:
    #     # if log:
    #     print("No JSON File written as data list is empty.")
    #     return

    try:

        filename = append_output_if_needed(filename)

        if not filename.endswith(".json"):
            filename = filename + ".json"

        _write_json(data, filename)

        if log:
            print(f"View written JSON file at {filename}")
        
    except PermissionError:
        prompt(
            f"{filename} is currently open in another application. Please close the the Application and press 'Enter' to save."
        )
        return write_json(data, filename, log)
    return filename
def write_temp_csv(data, log=True):
    return write_csv(data, "temp.csv", log)


def read_temp_csv():
    return read_csv("temp.csv")


def fix_csv_filename(filename):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".csv"):
        filename = filename + ".csv"
    return filename


def read_csv(filename):
    """
    Reads a CSV file and returns a list of dictionaries.

    :param filepath: str, the path to the CSV file
    :return: list of dictionaries
    """
    import csv

    filename = fix_csv_filename(filename)

    data = []
    with open(filename, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data


def get_fieldnames(data_list):
    fieldnames_dict = {}  # Initialize an empty dictionary
    for item in data_list:
        for key in item.keys():
            if key not in fieldnames_dict:
                fieldnames_dict[key] = (
                    None  # Set the value to None, we only care about the keys
                )
    return list(fieldnames_dict.keys())  # Convert the dictionary keys to a list


def convert_nested_to_json(input_list):
    """
    Iterates through a list of dictionaries and converts any nested dictionaries or lists
    within those dictionaries into JSON-formatted strings.

    :param input_list: The list of dictionaries to process.
    :return: A new list with dictionaries having nested dictionaries/lists converted to JSON strings.
    """
    output_list = []

    for item in input_list:
        processed_dict = {}
        for key, value in item.items():
            if isinstance(value, (dict, list, tuple, set)):
                # Convert the value to a JSON-formatted string if it's a dict or list
                processed_dict[key] = dumps(value)
            else:
                # Keep the value as is if it's not a dict or list
                processed_dict[key] = value
        output_list.append(processed_dict)

    return output_list


def remove_non_dicts(data):
    return [x for x in data if isinstance(x, dict)]


def write_csv(data, filename, log=True):
    """
    Save a list of dictionaries as a CSV file.

    Args:
        data: a list of dictionaries
        filename: the name of the CSV file to save
    """
    import csv

    data = clean_data(data)
    data = convert_nested_to_json(data)

    filename_new = append_output_if_needed(filename)


    if not filename_new.endswith(".csv"):
        filename_new = filename_new + ".csv"

    try:
        with open(filename_new, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = get_fields(data)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # write the header row
            writer.writerows(data)  # write each row of data
        if log:
            print(f"View written CSV file at {filename_new}")

    except PermissionError:
        prompt(
            f"{filename_new} is currently open in another application (e.g., Excel). Please close the the Application and press 'Enter' to save."
        )
        return write_csv(data, filename, log)
    return filename

def save_image(url, filename=None):
    import requests

    if filename is None:
        filename = url.split("/")[-1]
    response = requests.get(url)
    if response.status_code == 200:

        # Save the image in the output directory
        path = append_output_if_needed(filename)
        with open(relative_path(path), "wb") as f:
            f.write(response.content)
    else:
        print("Failed to download the image.")
        return path


def write_html(data, filename, log=True):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".html"):
        filename = filename + ".html"

    _write_html(data, filename)
    if log:
        print(f"View written HTML file at {filename}")
    return filename

def read_html(filename):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".html"):
        filename = filename + ".html"

    return _read_file(filename)


def write_temp_html(data, log=True):
   return write_html(data, "temp.html", log)


def read_temp_html():
    return read_html("temp.html")

def write_file(data, filename, log=True):

    filename = append_output_if_needed(filename)

    _write_file(data, filename)
    if log:
        print(f"View written file at {filename}")

    return filename
def read_file(filename):
    filename = append_output_if_needed(filename)

    return _read_file(filename)

def normalize_data(data):
    if data is None:
        return []
    elif isinstance(data, (list, set, tuple)):
        normalized_list = []
        for item in data:
            if item is None:
                continue  # Skip None items
            elif not isinstance(item, dict):
                item = {"data": item}  # Wrap non-dict items
            normalized_list.append(item)
        return normalized_list

    elif isinstance(data, dict):
        return [data]

    else:
        return [{"data": data}]
    
def normalize_dicts_by_fieldnames(data):
    fieldnames = get_fieldnames(data)
    filtered_data = []

    for item in data:
        filtered_item = {key: item.get(key, None) for key in fieldnames}
        filtered_data.append(filtered_item)

    return filtered_data

def clean_data(data):
    # Then, filter the normalized data to ensure each dict contains the same set of fieldnames
    return normalize_dicts_by_fieldnames(normalize_data(data))

def fix_excel_filename(filename):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".xlsx"):
        filename = filename + ".xlsx"
    return filename
def write_excel(data, filename, log=True):

    data = clean_data(data)
    data = convert_nested_to_json(data)

    try:
        filename = fix_excel_filename(filename)
        write_workbook(data, filename)

        if log:
            print(f"View written Excel file at {filename}")
    except PermissionError:
        prompt(f"{filename} is currently open in another application (e.g., Excel). Please close the the Application and press 'Enter' to save.")
        return write_excel(data, filename, log)
    return filename
def write_workbook(data, filename,  strings_to_urls = True):
    import xlsxwriter
    if strings_to_urls:
     workbook = xlsxwriter.Workbook(filename)
    else:
     workbook = xlsxwriter.Workbook(filename, {'strings_to_urls': False})
     
    worksheet = workbook.add_worksheet()

        # Write headers
    fieldnames = get_fields(data)
    worksheet.write_row(0, 0, fieldnames)

        # Write data
    row = 1
    for item in data:
        # Prevent Warnings and Handle Excel 65K Link Limit
        if worksheet.hlink_count > 65000:
            workbook.close()
            if os.path.exists(filename):
                os.remove(filename)
            return write_workbook(data, filename,strings_to_urls = False)
        values = list(item.values())
        worksheet.write_row(row, 0, values)
        row += 1

    workbook.close()
    return filename
def get_fields(data):
    if len(data) == 0:
        return []
    return list(data[0].keys())

def read_excel(filename):
    import openpyxl

    filename = fix_excel_filename(filename)

    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active

    data = []
    headers = [cell.value for cell in sheet[1]]

    for row in sheet.iter_rows(min_row=2):
        row_data = {}
        for cell, header in zip(row, headers):
            row_data[header] = cell.value
        data.append(row_data)

    return data

def write_temp_excel(data, log=True):
    return write_excel(data, "temp.xlsx", log)

def read_temp_excel():
    return read_excel("temp.xlsx")

def zip_files(filenames, output_filename="data", log=True):
    import zipfile

    # Ensure filenames is a list
    if not isinstance(filenames, list):
        filenames = [filenames]

    # Filter out any None or empty string filenames
    filenames = [f for f in filenames if f]

    # If no valid filenames, return early
    if not filenames:
        print("No files to zip.")
        return None

    # Prepare the output filename
    output_filename = append_output_if_needed(output_filename)
    if not output_filename.endswith(".zip"):
        output_filename += ".zip"

    try:
        with zipfile.ZipFile(output_filename, 'w') as zipf:
            for file in filenames:
                file = append_output_if_needed(file)
                if os.path.exists(file):
                    # Get the file name without the "output/" prefix
                    arcname =  os.path.basename(file) 
                    zipf.write(file, arcname=arcname)
                else:
                    print(f"Warning: File not found: {file}")

        if log:
            print(f"View written ZIP file at {output_filename}")
        return output_filename

    except PermissionError:
        prompt(f"{output_filename} is currently open in another application. Please close the application and press 'Enter' to retry.")
        return zip_files(filenames, output_filename, log)
    except zipfile.BadZipFile:
        print(f"Error: Unable to create zip file {output_filename}. It may be corrupted.")
        return None
    except Exception as e:
        print(f"Error while zipping files: {e}")
        return None