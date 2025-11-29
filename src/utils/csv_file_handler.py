import os
import csv


class CSVFileHandler:

    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers
        self.check_csv_file()

    def check_csv_file(self):
        """Create the CSV file with header if it does not exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def read_csv(self):
        """Return all rows (excluding header)."""
        with open(self.filename, 'r') as f:
            reader = csv.reader(f)
        return list(reader)

    def write_all_csv(self, rows):
        """Write file with header + rows."""
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            writer.writerows(rows)

    def add_to_csv(self, row):
        """Append a new row (data only)."""
        with open(self.filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
