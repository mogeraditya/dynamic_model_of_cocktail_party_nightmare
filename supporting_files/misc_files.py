import csv
import pandas 
import os

def load_parameters(file_dir):
    with open(file_dir, 'r') as csv_file:
        reader = pandas.read_csv(csv_file)
    return reader

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)