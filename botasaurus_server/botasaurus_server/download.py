from json import dumps
from bottle import HTTPResponse

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


def make_csv(fieldnames, results):
    import io
    import csv    

    buffer = io.StringIO()
    # Create a CSV writer that writes to the buffer
    # Note: 'newline=""' is necessary to prevent additional newlines on Windows
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)

    # Write the data to the buffer
    writer.writeheader()
    writer.writerows(results)

    # Rewind the buffer to the beginning
    buffer.seek(0)

    return buffer.getvalue()


def make_excel(fieldnames, results):
    import io
    import xlsxwriter

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("Sheet1")  # Specify the sheet name as "Sheet1"

    if results:
        # Write the headers
        for col, header in enumerate(fieldnames):
            worksheet.write(0, col, header)

        # Write the data rows
        for row, data in enumerate(results, start=1):
            for col, (key, value) in enumerate(data.items()):
                worksheet.write(row, col, value)

    workbook.close()
    buffer.seek(0)

    return buffer.getvalue()


def download_results(results, fmt, filename):

    headers = {}
    if fmt == "json":

        headers["Content-Type"] = "application/json"
        headers["Content-Disposition"] = f'attachment; filename="{filename}.json"'
        return HTTPResponse(body=dumps(results), status=200, headers=headers)
    
    results = convert_nested_to_json(results)

    if results:
        fieldnames = list(results[0].keys())
    else:
        fieldnames = []
    
    if fmt == "csv":
        headers["Content-Type"] = "text/csv"
        headers["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

        # Return the buffer's content as bytes
        body = make_csv(fieldnames, results)
        return HTTPResponse(body=body, status=200, headers=headers)
    elif fmt == "excel":
        headers["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        headers["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

        body = make_excel(fieldnames, results)
        return HTTPResponse(body=body, status=200, headers=headers)