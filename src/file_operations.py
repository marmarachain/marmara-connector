import os
import csv


class CSVFileHandler:

    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers
        self.check_csv_file()

    def check_csv_file(self):  # Check if the CSV file exists, if not create it with given headers.
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)

    def write_to_csv(self, data):  # Write data to the CSV file.
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

    def read_csv(self):  # Read the CSV file and return its contents.
        with open(self.filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header
            data = list(reader)
        return data

    def edit_csv(self, row_to_edit):  # Edit the CSV file by deleting the specified row.
        csv_data = self.read_csv()
        csv_data_ids = [int(row[0]) for row in csv_data]
        if int(row_to_edit[0]) in csv_data_ids:
            index = csv_data_ids.index(int(row_to_edit[0]))  # Find the index of the row
            csv_data[index] = row_to_edit
            self._rewrite_csv(csv_data)

    def delete_csv_row(self, row_to_delete):  # Edit the CSV file by deleting the specified row.
        csv_data = self.read_csv()
        csv_data_ids = [int(row[0]) for row in csv_data]
        if int(row_to_delete[0]) in csv_data_ids:
            index = csv_data_ids.index(int(row_to_delete[0]))  # Find the index of the row
            del csv_data[index]  # Delete the row
            self._rewrite_csv(csv_data)

    def _rewrite_csv(self, data):
        # Helper function to rewrite the entire CSV file with updated data.
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)  # Write header row
            writer.writerows(data)
