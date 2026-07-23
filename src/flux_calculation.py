import lime
from astropy.io import fits
from pathlib import Path
import numpy as np

from helper import *

def graph_fitted(path, filename):
    #Paths and names
    if not os.path.exists(path):
        os.makedirs(path)
    image_name = path + "/" + filter_out_filename_extension(filename)

    #building the plot
    ##mainly taken from the docs
    spec.fit.continuum(degree_list=[3, 6, 6], emis_threshold=[3, 2, 1.5], plot_steps=True, log_scale=True)
    spec.fit.bands(line, cont_source='adjacent')
    spec.plot.bands(fname=image_name + "_fitted")

def graph_matched_lines(path, filename):
    if not os.path.exists(path):
        os.makedirs(path)
    image_name = path + "/" + filter_out_filename_extension(filename)
    candidate_lines = spec.retrieve.lines_frame()
    matched_lines = spec.infer.peaks_troughs(candidate_lines, emission_type=True, sigma_threshold=3, plot_steps=True, log_scale=True)
    spec.plot.spectrum(rest_frame=True, fname=image_name, show_cont=True, bands=matched_lines)


#path to data
data_directory = Path("../data")

#all data file names
data_files = get_data_files("data")

redshifts = {"28074": 2.26, "40579": 3.1, "17775": 3.501, "154183": 3.55}
line = 'H1_10941A' #Paschen Gamma Line
flux_data = {}

#using LiME to calculate the H1 fluxes
for filename in data_files:
    #from https://lime-stable.readthedocs.io/en/latest/2_guides/0_creating_observations.html
    print("Processing " + filename + "...")
    file_path = data_directory/filename
    hdul = fits.open(file_path)
    wavelength, flux, flux_error = get_data(hdul)    
    wavelength = np.array([(w * u.um).to(u.AA).value for w in wavelength]) #units are originally in micrometers; using astropy to convert to angstrom
    flux, flux_error = fix_flux_units(flux, flux_error, wavelength)

    #Create the observation
    data_id = get_id(filename)
    print("Redshift Value:", redshifts[data_id])
    spec = lime.Spectrum(wavelength, flux, flux_error, redshift=redshifts[data_id], units_wave="AA", units_flux="FLAM")

    path = "../Fitted-Graphs"
    graph_fitted(path, filename)
    
    #plotting LiME Graphs
    path = "../Matched-Lines"
    graph_matched_lines(path, filename)
        
    try:
        profile_flux, profile_flux_error, intg_flux = calculate_flux(spec, line)
        flux_data[filename] = {
            "Flux": profile_flux,
            "Flux Error": profile_flux_error,
            "Integrated Flux": intg_flux,
        }
        print("profile flux: " + str(profile_flux))
        print("Flux error:", profile_flux_error)
    except Exception as e:
        print("Flux not found", e) #currently getting an error for one of the files not having any flux

write_data_to_json(flux_data, "../json_files/flux.json")

hdul.close()
