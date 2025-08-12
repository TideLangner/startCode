# model of linear degradation of m modules along n strings
# Tide Langner
# 12 August 2025
import pvlib.pvsystem
# --- Import
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

from pvmismatch import *
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# set location, timezone and altitude of solar array, named Kalkbult
location = Location(latitude=-30.09318567206943, longitude=24.13940478600872, tz='Africa/Johannesburg', altitude=1400, name='Kalkbult')

# extract sandia modules and CEC inverters databases
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')

# select particular module and inverter (create instance)
module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

# create temperature model instance (Sandia Array Performance Model)
temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']

# create the system
system = PVSystem(surface_tilt=45, surface_azimuth=0,
                  module_parameters=module, inverter_parameters=inverter,
                  temperature_model_parameters=temperature_parameters)

# create the model chain
modelchain = ModelChain(system, location)

# create time series for irradiance data for clear sky model
times = pd.date_range(start='2021-07-01', end='2021-07-07', freq='1min', tz=location.tz)

# create clear sky model
clear_sky = location.get_clearsky(times)
# plot
clear_sky.plot(figsize=(16,9))
plt.show()

# combine time series data with model chain
modelchain.run_model(clear_sky)
# plot
modelchain.results.ac.plot(figsize=(16,9)) # ac output of total system
plt.show()

# ended at end of ep.4
# https://www.youtube.com/watch?v=9wDhl6jyKmk&list=PLK7k_QaEmaHsPk_mwzneTE2VTNCpYBiky&index=5
