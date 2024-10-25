import csv
import math
from concurrent.futures import ThreadPoolExecutor

class BirthData:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = []  # Will hold all the rows of the CSV
        self.current_index = 0  # To track the current year
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Load CSV data into self.data
        # with open(csv_file, mode='r') as file:
        #     reader = csv.reader(file)
        #     next(reader)  # Skip the header
        #     self.data = list(reader)
        
    def load_data(self):
        """Load the CSV data asynchronously."""
        future = self.executor.submit(self._read_csv_file)
        return future
    
    def _read_csv_file(self):
        """Helper function to read CSV file and store data."""
        with open(self.csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            self.data = list(reader)

    def next_year(self):
        """Move to the next year if possible."""
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
        else:
            print("You are at the most recent year in the dataset.")

    def previous_year(self):
        """Move to the previous year if possible."""
        if self.current_index > 0:
            self.current_index -= 1
        else:
            print("You are at the earliest year in the dataset.")

    def jump_to_year(self, year):
        """Jump to a specific year if it exists."""
        for i, row in enumerate(self.data):
            if int(row[0]) == year:
                self.current_index = i
                return
        print(f"Year {year} not found in the dataset.")

    
    def data_to_balls(self, entry):
        # make each year's ball number proportion to each other
        # e.g. 2125000 -> 21; (21-10) / (30-10)
        entry[2] = math.ceil((float(entry[2])/100000 - 10)/20 * 100)
        entry[3] = math.ceil((float(entry[3])/100000 - 10)/20 * 100)
        return entry
    
    def read_current_entry(self):
        """Return the content of the current entry and print it out."""
        current_entry = self.data[self.current_index]
        current_entry_copy = current_entry.copy()
        print('og: ' + str(current_entry_copy))
        current_entry_copy = self.data_to_balls(current_entry_copy)
        print(current_entry_copy)
        return current_entry_copy
        



