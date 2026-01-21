import sys

import pandas as pd

sys.path.append("./dynamic_model")

from supporting_files.utilities import load_parameters

simulation_parameters = load_parameters(
    r"./dynamic_model/supporting_files/temporal_masking_fn.csv"
)
dict_1 = pd.read_csv(r"./dynamic_model/supporting_files/temporal_masking_fn.csv")
dict_2 = {}

for key in dict_1.keys()[1:]:
    dict_2[key] = dict_1[key].values

print(dict_1)
print(dict_2)
print(dict_2)
print(dict_2)
