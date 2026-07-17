import math
from pathlib import Path

from helper import *

def error_quadrature(error1, error2):
    overall_error = math.sqrt((error1 * error1) + (error2 * error2))
    return overall_error

def fractional_error_quadrature(error1, quantity1, error2, quantity2):
    quotient = quantity1/quantity2
    percent_error1 = error1/quantity1
    percent_error2 = error2/quantity2
    overall_error = quotient * error_quadrature(percent_error1, percent_error2)
    return overall_error

#path to data
research_directory = Path("/home/ianbishop/research-internship/")
data_directory = Path(research_directory/"data")

#all data file names
data_files = os.listdir(data_directory)

He1_fluxes = {"28074": 82.11e-18, "40579": 70e-18, "17775": 24.579e-18, "154183": 2.7e-18} #these fluxes were already calculated by previous research
#has both narrow and broad; narrow at index 0, broad at index 1
#ID 40579 not included here since it already gives the total flux errors
He1_errors_positive = {"28074": [0.51e-18, 1.2e-18], "17775": [0.96e-18, 2.126e-18], "154183": [0.3e-18, 0.5e-18]} #taken from papers
He1_errors_negative = {"28074": [-0.52e-18, -1.3e-18], "17775": [-0.96e-18, -2.126e-18], "154183": [-0.3e-18, -0.5e-18]} #also taken from papers

He1_total_errors_positive = {}
He1_total_errors_negative = {}

ratio_errors_positive = {}
ratio_error_negative = {}

for filename in data_files:
    try:
        name = get_id(filename)
        total_error_positive = error_quadrature(He1_errors_positive[name][0], He1_errors_positive[name][1])
        total_error_negative = error_quadrature(He1_errors_negative[name][0], He1_errors_negative[name][1])
        He1_total_errors_positive[name] = total_error_positive
        He1_total_errors_negative[name] = total_error_negative
    except Exception as e:
        print("something went wrong", e)

data = {}
print("data_files:", data_files)
for filename in data_files:
    try:
        name = get_id(filename)
        H1_flux = read_json("flux.json", filename, "Flux")
        H1_flux_error = read_json("flux.json", filename, "Flux Error")

        #Helium first, then hydrogen for the ratio
        ratio_error_positive = fractional_error_quadrature(
            He1_total_errors_positive[name],
            He1_fluxes[name],
            H1_flux,
            H1_flux_error
        )

        ratio_error_negative = fractional_error_quadrature(
            He1_total_errors_negative[name],
            He1_fluxes[name],
            H1_flux,
            H1_flux_error
        )

        data[filename] = {
            "Positive Error": ratio_error_positive,
            "Negative Error": ratio_error_negative
        }
        print("data piece:", data[filename])
    except Exception as e:
        print("something else went wrong", e)

print("data:", data)
write_data_to_json(data, "flux_error.json")
