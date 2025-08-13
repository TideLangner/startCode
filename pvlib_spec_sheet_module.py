# module model according to given spec sheet
# Tide Langner
# 13 August 2025

# Import
import pvlib
from pvlib.location import Location
import pandas as pd

# Define module
celltype = 'polySi'
p_max = 290
v_mp = 36.4
i_mp = 7.97
v_oc = 44.9
i_sc = 8.89
temp_coeff_pmax = -0.0047*p_max
temp_coeff_voc = -0.0040*v_oc
temp_coeff_isc = 0.0005*i_sc
cells_in_series = 6*12
temp_ref = 25

location = Location(latitude=-30.09318567206943, longitude=24.13940478600872,
                    tz='Africa/Johannesburg',
                    altitude=1400, name='Kalkbult')

surface_tilt=45
surface_azimuth=0

start = '2020-07-01 00:00'
end = '2020-07-02 23:00'

poa_data_2020 = pd.read_csv('poa_data_2020_io.csv', index_col=0)
poa_data_2020.index = pd.date_range(start='2020-01-01',
                                    periods=len(poa_data_2020.index),
                                    freq='h')
poa_data = poa_data_2020[start:end]

print(poa_data_2020.head())
