from json import dumps

from .errors import DownloadResponse
from botasaurus.output import convert_nested_to_json, convert_nested_to_json_for_excel



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


def make_excel(fieldnames, results,  strings_to_urls = True):
    import io
    import xlsxwriter

    buffer = io.BytesIO()
    if strings_to_urls:
     workbook = xlsxwriter.Workbook(buffer)
    else:
     workbook = xlsxwriter.Workbook(buffer, {'strings_to_urls': False})
    
    worksheet = workbook.add_worksheet("Sheet1")  # Specify the sheet name as "Sheet1"

    if results:
        # Write the headers
        for col, header in enumerate(fieldnames):
            worksheet.write(0, col, header)

        row = 1
        for item in results:
            # Prevent Warnings and Handle Excel 65K Link Limit
            if worksheet.hlink_count > 65000:
                workbook.close()
                buffer.close()
                
                return make_excel(fieldnames, results, strings_to_urls=False)
            values = list(item.values())
            worksheet.write_row(row, 0, values)
            row += 1

    workbook.close()
    buffer.seek(0)

    value = buffer.getvalue()
    buffer.close()
    return value


def download_results(results, fmt, filename):

    headers = {}
    if fmt == "json":

        headers["Content-Type"] = "application/json"
        headers["Content-Disposition"] = f'attachment; filename="{filename}.json"'
        return DownloadResponse(body=dumps(results), status=200, headers=headers)
    
    

    if results:
        fieldnames = list(results[0].keys())
    else:
        fieldnames = []
    
    if fmt == "csv":
        results = convert_nested_to_json(results)
        headers["Content-Type"] = "text/csv"
        headers["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

        # Return the buffer's content as bytes
        body = make_csv(fieldnames, results)
        return DownloadResponse(body=body, status=200, headers=headers)
    elif fmt == "excel":
        results = convert_nested_to_json_for_excel(results)
        headers["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        headers["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

        body = make_excel(fieldnames, results)
        return DownloadResponse(body=body, status=200, headers=headers)