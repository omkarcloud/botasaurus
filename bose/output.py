import requests
import csv
from .utils import relative_path, write_json, read_json, write_html

class Output:

    def read_json(filename):
        if not filename.startswith("output/"):
            filename = "output/" +  filename

        if not filename.endswith(".json"):
            filename = filename + ".json"

        return read_json(filename)

    def write_json(data, filename):
        if len(data) == 0:
            print("Data is empty.")
            return

        if not filename.startswith("output/"):
            filename = "output/" +  filename

        if not filename.endswith(".json"):
            filename = filename + ".json"

        write_json(data, filename)
        print(f"View written JSON file at {filename}")        

    def write_csv(data, filename):
        
        """
        Save a list of dictionaries as a CSV file.

        Args:
            data: a list of dictionaries
            filename: the name of the CSV file to save
        """
        
        if type(data) is dict:
            data = [data]

        if len(data) == 0:
            print("Data is empty.")
            return

        if not filename.startswith("output/"):
            filename = "output/" +  filename

        if not filename.endswith(".csv"):
            filename = filename + ".csv"

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()  # get the fieldnames from the first dictionary
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # write the header row
            writer.writerows(data)  # write each row of data
        print(f"View written CSV file at {filename}")     


    def read_finished_json():
        return Output.read_json("finished.json")

    def write_finished_json(data):
        return Output.write_json(data, 'finished.json')


    def write_finished_csv(data):
        return Output.write_csv(data, 'finished.csv')

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
        
    def write_html(data, filename):
        if not filename.startswith("output/"):
            filename = "output/" +  filename

        if not filename.endswith(".html"):
            filename = filename + ".html"

        write_html(data, filename)
        print(f"View written HTML file at {filename}")



    def write_file(data, filename):
        if not filename.startswith("output/"):
            filename = "output/" +  filename


        write_html(data, filename)
        print(f"View written file at {filename}")



