import matplotlib.pyplot as plt
import os
import re
import json

def get_data(hdul):
    wavelength = hdul[1].data["wave"]
    flux = hdul[1].data["flux"]
    flux_error = hdul[1].data["err"]
    return wavelength, flux, flux_error

def print_hdul_headers(hdul):
    print(hdul[1].columns)

def plot_data(wavelength, flux, path, data_id):
    plt.plot(wavelength, flux, drawstyle = 'steps-mid')
    plt.xlabel("Wavelength($\\mu$m)")
    plt.ylabel("Flux(uJy)") #note to self: be sure to normalize units
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    #plt.xlim(4, 4.5) #scaling to see the bins
    plt.savefig(path + "/" + data_id + '_graph.png', dpi=150) #saving plot as an image

def get_id(filename):
    inital_filtering = re.search(r"lp_(\d+)_(\d+)", filename)
    data_id = inital_filtering.group(2) 
    return data_id

def filter_out_filename_extension(filename):
    return filename.split(".")[0]

def write_data_to_json(data, json_file):
    print("Writing to " + json_file + "...")
    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)
    print("Writing complete.")

def read_json(json_file, flux_id, item):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data[flux_id][item]

