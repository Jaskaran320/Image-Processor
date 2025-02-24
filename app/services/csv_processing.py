import csv

def validate_csv_format(csv_content: bytes) -> tuple[bool, str | None]:
    try:
        csv_text = csv_content.decode('utf-8')
        reader = csv.reader(csv_text.splitlines())
        header = next(reader)
        if header != ['S. No.', 'Product Name', 'Input Image Urls']:
            return False, "CSV header is incorrect. Expected ['S. No.', 'Product Name', 'Input Image Urls']"
        for row in reader:
            if len(row) != 3:
                return False, "Each row should have 3 columns."
            try:
                int(row[0])
            except ValueError:
                return False, "Serial Number (S. No.) should be an integer."
            if not row[1]:
                return False, "Product Name cannot be empty."
            if not row[2]:
                return False, "Input Image Urls cannot be empty."
        return True, None
    except Exception as e:
        return False, f"CSV validation failed: {str(e)}"