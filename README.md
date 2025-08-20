---
# Dynamic Model of Cocktail Party Nightmare
 Implementing a dynamic model of the cocktail party nightmare problem :)
---

## Installation of environment

Use the environment_cocktail_3.yml alongside conda in order to install all the pre-requistite packages needed to run these simulations. This can be come running;
> conda env create -f environment_cocktail_3.yml

---
## Parameters of the model 
For detailed description of the parameters used in model, please refer to ./dynamic_model/supporting_files/make_common_parameters.py.
---

## How to run one instance of the simulation
1. Initialize your parameters.
    ./paramsets/ contains a set of example paramset files. Fill in your desired parameter values into the cells of the csv file. Be sure to stick to S.I. units while entering parameters. 

2. Change directories in the simulation.py file
    change the OUTPUT_DIR (directory where the output is to be saved) and the PARAMETER_FILE_DIR (directory of the parameter file)

3. Run the simulation.py file
    this runs one instance of the simulation. 

4. Change directories in the plotter.py file
    change the OUTPUT_DIR (directory where the output of the simulation is saved) and SAVE_SIMULATION (False if animation need not be saved, else is the directory where the animation needs to be saved)

5. Run plotter.py 
    animation will pop out of a video after it is processed!
---

## How to run for varying parameters
1. Run ./dynamic_model/supporting_files/make_common_parameters.py to generate the template parameter file. This parameter file is stored in ./dynamic_model/paramsets/common_parameters.csv and contains the defalt values of all the parameters.
2. An example to generate multiple paramsets is given in ./dynamic_model/paramsets/effect_of_group_size/make_paramset_effect_of_group_size.py. This can be modified for your specific use case.
3. In order to run the simulation over the newly generated parameter files, head to ./dynamic_model/simulation_multiple_parameters.py and change the following variables
    1. 