# define one instance somehow; itll be parse all the folders in storage area for example. lets care about details later

import numpy as np
import os
import glob

output_dir= "./test_storage/*"
list_of_bats_in_simulation= glob.glob(output_dir)
list_of_bats_in_simulation= [int(i[-1]) for i in list_of_bats_in_simulation]
print(list_of_bats_in_simulation)
# for bat_id in list_of_bats_in_simulation:
#     list_of_saved_files= 

path_of_a_file= "./test_storage/0/bat_0_received_sounds_snapshot_at_time_0.580.npy"
array= np.load(path_of_a_file, allow_pickle=True)
# print(array)
sublist_array_1= [i for i in array if i["emitter_id"]==2 and i["type"]=="echo" and i["reflected_from"]=="bat_1" ]
sublist_array_0= [i for i in array if i["emitter_id"]==2 and i["type"]=="echo" and i["reflected_from"]=="bat_0" ]
# print(sublist_array_0[0:7])
arrr= [i["sound_object_id"] for i in sublist_array_0[0:7]]
print(arrr)
# print(sublist_array_1[0:2])