# module model according to given spec sheet
# Tide Langner
# 13 August 2025

# Import
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
import pandas as pd
from scipy.signal import freqs
import matplotlib.pyplot as plt

# Define module
celltype = 'polySi'
p_max = 290
v_mp = 36.4
i_mp = 7.97
v_oc = 44.9
i_sc = 8.89
temp_coeff_pmax = -0.0047   # *p_max # if using pv_watts method
temp_coeff_voc = -0.0040*v_oc # if using pv_watts method
temp_coeff_isc = 0.0005*i_sc # if using pv_watts method
cells_in_series = 6*12
temp_ref = 25

location = Location(latitude=-30.09318567206943, longitude=24.13940478600872,
                    tz='Africa/Johannesburg',
                    altitude=1400, name='Kalkbult')

surface_tilt=45
surface_azimuth=0

start = '2020-01-01 12:00'
end = '2020-01-07 12:00'

poa_data_2020 = pd.read_csv('poa_data_2020_io.csv', index_col=0)
poa_data_2020.index = pd.date_range(start='2020-01-01',
                                    periods=len(poa_data_2020.index),
                                    freq='h')
poa_data = poa_data_2020[start:end]
# print(poa_data_2020.head())

# solar position throughout time [start:end]
solar_pos = location.get_solarposition(times=pd.date_range(start=start, end=end, freq='h'))

# angle of incidence
aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth, solar_pos.apparent_zenith, solar_pos.azimuth)

# incident angle modifier
iam = pvlib.iam.ashrae(aoi)

# effective irradiance
effective_irradiance = poa_data['poa_direct'] * iam + poa_data['poa_diffuse']

# effective temperature on module
temp_cell = pvlib.temperature.faiman(poa_data['poa_global'], poa_data['temp_air'], poa_data['wind_speed'])


# --- CEC module database

# load the CEC module database (bundled with pvlib)
cec = pvlib.pvsystem.retrieve_sam('CECMod')

# find the exact key for your module (print a few candidates to confirm)
candidates = [k for k in cec.columns
              if 'JINKO' in k.upper() and '290' in k and 'P' in k and '72' in k]
# print(candidates)   # e.g. ['Jinko_Solar_JKM290P_72']

# pick the match from the printed list
mod = cec[candidates[0]]

# pull inputs
IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(
    effective_irradiance=effective_irradiance,
    temp_cell=temp_cell,
    alpha_sc=mod['alpha_sc'],
    a_ref=mod['a_ref'],
    I_L_ref=mod['I_L_ref'],
    I_o_ref=mod['I_o_ref'],
    R_sh_ref=mod['R_sh_ref'],
    R_s=mod['R_s'],
    Adjust=mod.get('Adjust', 0)  # some entries may omit Adjust; default 0
)

'''
# commented out because of error 6parsolve simulation error 
# : Could not solve, sanity check failed (-33): abs((P - Pmp) / Pmp) > 0.015

# single diode models for giving more values for IV curves
I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = pvlib.ivtools.sdm.fit_cec_sam(
    celltype=celltype,
    v_mp=v_mp,
    i_mp=i_mp,
    v_oc=v_oc,
    i_sc=i_sc,
    alpha_sc=temp_coeff_isc,
    beta_voc=temp_coeff_voc,
    gamma_pmp=temp_coeff_pmax,
    cells_in_series=cells_in_series,
    temp_ref=temp_ref
)

cec_params = pvlib.pvsystem.calcparams_cec(effective_irradiance,
                                           temp_cell,
                                           temp_coeff_isc,
                                           I_L_ref,
                                           I_o_ref,
                                           R_sh_ref,
                                           R_s,
                                           Adjust
)
'''

mpp = pvlib.pvsystem.max_power_point(IL, I0, Rs, Rsh, nNsVth, method='newton')  # DC result 1 module
print(mpp)
mpp.plot(figsize=(16,8))
plt.title('DC Power 1 Module')
plt.show()

# Now that we have created the module, we can create the system
system = PVSystem(modules_per_string=5, strings_per_inverter=1)

# DC results when scaled
dc_scaled = system.scale_voltage_current_power(mpp)
dc_scaled.plot(figsize=(16,8))
plt.title('DC Power 5 Modules')
plt.show()

# Define inverter from database
cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
inverter = cec_inverters['ABB__PVI_3_0_OUTD_S_US_208V']

# AC results for 1 module
ac_results = pvlib.inverter.sandia(
    v_dc=dc_scaled.v_mp,
    p_dc=dc_scaled.p_mp,
    inverter=inverter
)

# AC results when scaled
ac_scaled = pvlib.inverter.pvwatts(pdc=dc_scaled.p_mp, pdc0=5000,
                                   eta_inv_nom=0.961, eta_inv_ref=0.9637)  # inverter numbers random here
ac_scaled.plot(figsize=(16,8))
# or ac_results.plot(figsize(16,8)) for AC results using inverter from database
plt.title('AC Power')
plt.show()

'''
# DC output of module at hand
result_dc = pvlib.pvsystem.pvwatts_dc(effective_irradiance, temp_cell,
                                      pdc0=p_max, gamma_pdc=temp_coeff_pmax,
                                      temp_ref=25)

# DC results
result_dc.plot(figsize=(16,8))
plt.title('DC Power')
plt.show()

# AC results
result_ac = pvlib.inverter.pvwatts(pdc=result_dc, pdc0=500,
                                   eta_inv_nom=0.961, eta_inv_ref=0.9637)  # inverter numbers random here

result_ac.plot(figsize=(16,8))
plt.title('AC Power')
plt.show()
'''
