import csv
import pandas 
import os



def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def convert_txt_to_int_or_float(txt):
    try:
        k = float(txt)
        if k%1 ==0:
            return int(k)
        return k

    except ValueError:
        return txt
    
def load_parameters(file_dir):
    with open(file_dir, 'r') as csv_file:
        reader = pandas.read_csv(csv_file)
    output_df= pandas.DataFrame()
    for key in reader.keys():
        value= reader[key][0]
        value= convert_txt_to_int_or_float(value)
        output_df[key] = [value]
    return output_df

# file_dir= r"../paramsets/mycsvfile.csv"
# df= load_parameters(file_dir)
# print(df)
# print(df["NUM_BATS"][0])
# print(type(df["NUM_BATS"][0]))