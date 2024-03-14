from bottle import HTTPResponse
import xlsxwriter
import io
import csv
import json
from botasaurus.output import convert_nested_to_json


def make_csv(fieldnames, results):
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
        return HTTPResponse(body=json.dumps(results), status=200, headers=headers)
    
    results = convert_nested_to_json(results)

    if results:
        fieldnames = results[0].keys()
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