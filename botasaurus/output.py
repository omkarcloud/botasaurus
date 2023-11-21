import requests
import csv
from .utils import  read_file as _read_file, relative_path, write_json as _write_json, read_json as _read_json, write_html as _write_html, write_file as _write_file
from .beep_utils import prompt


def is_slash_not_in_filename(filename):
    return '/' not in filename and '\\' not in filename

def append_output_if_needed(filename):
    filename = str(filename).strip()
    if is_slash_not_in_filename(filename):
        return "output/" +  filename
    return filename


def fix_json_filename(filename):
    filename = append_output_if_needed(filename)

    if not filename.endswith(".json"):
        filename = filename + ".json"
    return filename

def read_json(filename):
        filename = fix_json_filename(filename)

        return _read_json(filename)


def file_exists(filename):
        filename = append_output_if_needed(filename)

        try:
            with open(filename, 'r'):
                return True
        except FileNotFoundError:
            return False

def write_json(data, filename, log = True):
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
            prompt(f"{filename} is currently open in another application. Please close the the Application and press 'Enter' to save.")
            write_json(data, filename, log)


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

        filename = fix_csv_filename(filename)

        data = []
        with open(filename, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data

def get_fieldnames(data_list):
    fieldnames = []
    for item in data_list:
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    return fieldnames

def write_csv(data, filename, log = True):
        
        """
        Save a list of dictionaries as a CSV file.

        Args:
            data: a list of dictionaries
            filename: the name of the CSV file to save
        """
        
        if type(data) is dict:
            data = [data]



        filename_new = append_output_if_needed(filename)

        
        if not filename_new.endswith(".csv"):
            filename_new = filename_new + ".csv"

        # if data is None or len(data) == 0:
            # if log:
            # print("No CSV File written as data list is empty.")
            # print("Data is empty.")
            # return

        try:
            with open(filename_new, 'w', newline='', encoding='utf-8') as csvfile:
                # fieldnames = data[0].keys()  # get the fieldnames from the first dictionary
                fieldnames = get_fieldnames(data)
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # write the header row
                writer.writerows(data)  # write each row of data
            if log:
                print(f"View written CSV file at {filename_new}")     

        except PermissionError:
            prompt(f"{filename_new} is currently open in another application (e.g., Excel). Please close the the Application and press 'Enter' to save.")
            write_csv(data, filename, log)


def save_image(url, filename = None):
        if filename is None:
            filename = url.split("/")[-1]
    
        response = requests.get(url)
        if response.status_code == 200:
            # Extract the filename from the URL
            output_dir = "output"

            # Save the image in the output directory
            path = f'{output_dir}/{filename}'
            with open(relative_path(
                path, 0), "wb") as f:
                f.write(response.content)
        else:
            print("Failed to download the image.")
            return path
        
def write_html(data, filename, log = True):
        filename = append_output_if_needed(filename)

        if not filename.endswith(".html"):
            filename = filename + ".html"

        _write_html(data, filename)
        if log:        
            print(f"View written HTML file at {filename}")


def read_html(filename):
        filename = append_output_if_needed(filename)

        if not filename.endswith(".html"):
            filename = filename + ".html"

        return _read_file(filename)


def write_file(data, filename, log = True):

        filename = append_output_if_needed(filename)


        _write_file(data, filename)
        if log:  
            print(f"View written file at {filename}")


def read_file(filename):
        filename = append_output_if_needed(filename)

        return _read_file(filename)

