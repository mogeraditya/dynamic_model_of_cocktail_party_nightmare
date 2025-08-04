import csv
import pandas 

def load_parameters(file_dir):
    with open(file_dir, 'r') as csv_file:
        reader = pandas.read_csv(csv_file)
    return reader
    
load_parameters("paramsets/mycsvfile.csv")
