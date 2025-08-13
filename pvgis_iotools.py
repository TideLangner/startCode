import pandas as pd
import pvlib

poa_data_2020, meta = pvlib.iotools.get_pvgis_hourly(
    latitude=-30.09318567206943, longitude=24.13940478600872,
    start=2020, end=2020,
    raddatabase='PVGIS-SARAH3', components=True,
    surface_tilt=45, surface_azimuth=180,    # 180 = North for PVGIS
    outputformat='json', usehorizon=True, userhorizon=None,
    pvcalculation=False, peakpower=None, pvtechchoice='crystSi',
    mountingplace='free', loss=0, trackingtype=0,
    optimal_surface_tilt=False, optimalangles=False,
    url='https://re.jrc.ec.europa.eu/api/v5_3/', map_variables=True, timeout=30)


# Use this for keeping all columns
poa_data_2020['poa_diffuse'] = poa_data_2020['poa_sky_diffuse'] + poa_data_2020['poa_ground_diffuse']
poa_data_2020['poa_global'] = poa_data_2020['poa_diffuse'] + poa_data_2020['poa_direct']

# Extract necessary columns
keep_cols = ['poa_global', 'poa_direct', 'poa_diffuse', 'temp_air', 'wind_speed']
poa_data_2020 = poa_data_2020[keep_cols]

print(poa_data_2020)

poa_data_2020.to_csv('poa_data_2020_io.csv')