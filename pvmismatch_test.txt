#%%
#!/usr/bin/env python3
"""
Demonstration script for pvmismatch >= 4.1:
"""

#%%
from pvmismatch import *  # this imports everything we need
from matplotlib import pyplot as plt  # now lets make some plots
import numpy as np
import pandas as pd

#%% Simple example

pvsys = pvsystem.PVsystem(numberStrs=30, numberMods=21)  # makes the system
plt.ion()  # this turns on interactive plotting
f = pvsys.plotSys()  # creates a fig

print(f'{pvsys.Vmp=}')  # max voltage [V]
print(f'{pvsys.Imp=}')  # max current [A]
print(f'{pvsys.Pmp=}')
print(f'{pvsys.FF=}')
print(f'{pvsys.eff=}')
print(f'{pvsys.Voc=}')
print(f'{pvsys.Isc=}')

print(f'{pvsys.numberMods=}')
print(f'{pvsys.numberStrs=}')

#%%
fig, ax = plt.subplots(1,1)
ax.plot(pvsys.Vsys/pvsys.Vmp, pvsys.Psys/pvsys.Pmp)
ax.grid()

#%%
pvsys.setSuns(1.)  # sets the suns to 1 sun
power_per_module_before = pvsys.Pmp / sum(pvsys.numberMods)

pvsys.setSuns(1.)  # sets the suns to 1 sun
pvsys.setSuns({0: {0: 0.0001}})  # Shade module 1 in string 1

power_per_module_after = pvsys.Pmp / sum(pvsys.numberMods)

print(f'{power_per_module_before=}')
print(f'{power_per_module_after=}')

module_eq_diff = (power_per_module_before - power_per_module_after) * sum(pvsys.numberMods) / power_per_module_before
print(f'{module_eq_diff=}')

#%% Example of partial shading and partial heating
# https://url.za.m.mimecastprotect.com/s/bXKkCBgX56fV0WN4oSzfxs2nC3x
pvsys = pvsystem.PVsystem(numberStrs=2, numberMods=8)  # makes the system
pvsys.setSuns({0: {0: [(0.2, ) * 8, (11, 12, 35, 36, 59, 60, 83, 84)]}})

pvsys.setTemps(50. + 273.15)
pvsys.setTemps({0: {0: [(100. + 273.15, ) * 8, (11, 12, 35, 36, 59, 60, 83, 84)]}})


f_shade = pvsys.plotSys()
print(f'{pvsys.Pmp=}')

[pvsys.pvmods[0][0].pvcells[_] for _ in (11, 12, 35, 36, 59, 60, 83, 84)]


#%% Effect of shading diode or bottom row of cells
numberStrs = 200
numberMods = 21
num_degraded_modules = 21 #in singel string
shading_type = 'bottom_row' # 'diode' or 'bottom_row'
diffuse_fraction = 0.2 # Only used for 'bottom_row', diode fully shaded
pvsys = pvsystem.PVsystem(numberStrs=numberStrs, numberMods=numberMods, pvmods=pvmodule.PVmodule(cell_pos=pvmodule.STD72))  # makes the system

pvsys.setTemps(50. + 273.15)
before_shade = pvsys.Pmp

# Shade one diode 
for n in range(num_degraded_modules):
    if shading_type == 'diode':
        pvsys.setSuns({0: {n: [(0.001, ) * 24, tuple(range(24))]}})
    elif shading_type == 'bottom_row':        
        pvsys.setSuns({0: {n: [(diffuse_fraction, ) * 6, (11, 12, 35, 36, 59, 60)]}})

after_shade = pvsys.Pmp
# pvsys.setTemps({0: {0: [(100. + 273.15, ) * 8, (11, 12, 35, 36, 59, 60)]}})

f_shade = pvsys.plotSys()
if shading_type == 'diode':
    module_power_remaining = 0.667
elif shading_type == 'bottom_row':
    module_power_remaining = 0.2

module_equivalent_loss = (before_shade - after_shade)/(before_shade/(numberStrs*numberMods))
print(f'{pvsys.Pmp=}')
print(f'Lost module eq: {module_equivalent_loss=}')
Pnom_reduction = 1*(1 - module_power_remaining) #num of degraded modules is 1
print(f'Mismatch: {(module_equivalent_loss/num_degraded_modules)/Pnom_reduction - 1}')
print(f'{module_equivalent_loss/num_degraded_modules=}')
# [pvsys.pvmods[0][0].pvcells[_] for _ in (11, 12, 35, 36, 59, 60, 83, 84)]

#%% Example of plotting modules and cells
f_mod00 = pvsys.pvmods[0][0].plotMod()
f_modd00_cells = pvsys.pvmods[0][0].plotCell()

# np.interp(pvsys.Vmp, pvsys.pvstrs[0].Vstring, pvsys.pvstrs[0].Istring)

#%% Loop through effect of shading output from 1 module in single string
num_strings_list = np.unique(np.logspace(0, np.log10(50), num=10, dtype=int))
module_eq_diff_list = []

num_modules_per_string = 20
for num_strings in num_strings_list:
    
    pvsys = pvsystem.PVsystem(numberStrs=int(num_strings), numberMods=num_modules_per_string)  # makes the system
    
    # pvsys.setSuns(1.)  # Default, but making it explicit
    pvsys.setTemps(50. + 273.15) # Operating temperature of 50°C

    power_per_module_before = pvsys.Pmp / sum(pvsys.numberMods)
    pvsys.setSuns({0: {0: 0.9}})  # sets the suns to 1 sun for string 0, module 0
    
    power_per_module_after = pvsys.Pmp / sum(pvsys.numberMods)
    module_eq_diff = (power_per_module_before - power_per_module_after) * sum(pvsys.numberMods) / power_per_module_before
    print(f'{module_eq_diff=}')
    module_eq_diff_list.append(module_eq_diff)

fig, ax = plt.subplots()
ax.plot(num_strings_list, module_eq_diff_list)


# %% Recreate "Simulated Impact of Shortened Strings in Commercial and Utility-Scale Photovoltaic Arrays"
''' NB: This only shades modules, it does not remove them - see next example'''
from time import time

start=time()

n_modules_missing = 1
n_strings_missing = 1

underperformance_fraction = 0.01 #Between 0.01 and 1, do not axcept exactly 0

pvsys = pvsystem.PVsystem(numberStrs=30, numberMods=21)  # makes the system
# pvsys.setSuns(0.8) 800 W/m2
pvsys.setTemps(50. + 273.15)
power_per_module_before = pvsys.Pmp / sum(pvsys.numberMods)

for n in range(n_strings_missing):
    for m in range(n_modules_missing):
        pvsys.setSuns({n: {m: underperformance_fraction}})

power_per_module_after = pvsys.Pmp / sum(pvsys.numberMods)
module_eq_diff = (power_per_module_before - power_per_module_after) * sum(pvsys.numberMods) / power_per_module_before


missing_module_effect = n_modules_missing*n_strings_missing*(1-underperformance_fraction)
print(f'{missing_module_effect=}')
print(f'{module_eq_diff=}')
print(f'Multiplier = {module_eq_diff/missing_module_effect}')
end=time()
print(f'{end-start=}')


#%% Create cell with series or shunt resistance
# mycell = pvcell.PVcell(Rs=0.04)
mycell = pvcell.PVcell(Rsh=0.25)
pvm = pvmodule.PVmodule(cell_pos=pvmodule.STD96, pvcells=[mycell]*96)
print(f'Fill factor = {max(pvm.Pmod)/(np.median(pvm.Isc)*np.median(pvm.Voc))}')
pvm.plotMod()


#%% Example where one can degrade modules in strings or remove them - should also add random variation...?
num_strings_list = [30] #np.unique(np.logspace(0, np.log10(500), num=13, dtype=int))
results =  []
# num_module_list = np.linspace(1, 21, num=11, dtype=int)
# pvconst = pvconstants.PVconstants(npts=1000) # None

# num_strings = 100
num_modules_per_string = 21
num_degraded_modules = 1
num_degraded_strings = 1
missing_module = False

cell_std = pvcell.PVcell()

# cell_degraded = pvcell.PVcell(Rs=0.04)
cell_degraded = pvcell.PVcell(Rsh=0.25)
# cell_degraded = pvcell.PVcell(Rs=0.03, Rsh=0.375)

module_std = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell_std]*72)
module_degraded = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell_degraded]*72)


if missing_module:
    module_power_remaining = 0 
else:   
    module_power_remaining = max(module_degraded.Pmod)/max(module_std.Pmod)

print(f'{module_power_remaining=}')

for num_strings in num_strings_list:
# for num_degraded_modules in num_module_list:
    
    string_std = pvstring.PVstring(pvmods=[module_std]*num_modules_per_string)
    
    modules_list = [module_degraded] * num_degraded_modules + [module_std] * (num_modules_per_string - num_degraded_modules)

    if missing_module:
        string_degraded = pvstring.PVstring(pvmods=[module_std]*(num_modules_per_string-num_degraded_modules))
    else:
        string_degraded = pvstring.PVstring(pvmods=modules_list)

    pvsys_std = pvsystem.PVsystem(pvstrs=[string_std]*num_strings)  # makes the system
    pvsys_degraded = pvsystem.PVsystem(pvstrs=[string_degraded]*num_degraded_strings + [string_std]*(num_strings - num_degraded_strings))  # makes the system

    # pvsys.setSuns(0.8) 800 W/m2
    pvsys_std.setTemps(50. + 273.15)
    pvsys_degraded.setTemps(50. + 273.15)

    power_per_module_std = pvsys_std.Pmp / sum(pvsys_std.numberMods)
    #dividing on standard array length to get power of the full string length
    power_per_module_degraded = pvsys_degraded.Pmp / sum(pvsys_std.numberMods)

    print(f'Pdegraded/Pstd = {module_power_remaining}')
    print(f'{power_per_module_std=}')
    print(f'{power_per_module_degraded=}')
    module_eq_diff = (power_per_module_std - power_per_module_degraded) * sum(pvsys_std.numberMods) / power_per_module_std

    Pnom_reduction = num_degraded_modules*num_degraded_strings*(1 - module_power_remaining)
    print(f'{Pnom_reduction=}')
    print(f'{module_eq_diff=}')
    print(f'Mismatch = {module_eq_diff/Pnom_reduction - 1}')
    results.append(module_eq_diff/Pnom_reduction - 1)

#%%
fig, ax = plt.subplots()
ax.plot(num_strings_list, results)
ax.set(xlabel='Number of strings', ylabel='Mismatch [%]')

#%%
# Find string power for system maximum power for string with given index (0 is degraded)
string_index = 0
string_power = np.interp(pvsys_degraded.Vmp, pvsys_degraded.pvstrs[string_index].Vstring, pvsys_degraded.pvstrs[string_index].Pstring)

# %%
''' Example below does not work, because I get pvsys.update to work when removing strings, but not modules'''
# num_modules_per_string = 21
# num_strings = 30
# num_missing_modules = 1
# num_strings_with_missing_modules = 1
# nom_modules_total = num_modules_per_string*num_strings
# num_strings_with_missing_modules*num_missing_modules

# cell_std = pvcell.PVcell()

# pvsys = pvsystem.PVsystem(numberStrs=num_strings, numberMods=num_modules_per_string)


# pvsys.setTemps(50. + 273.15)

# power_per_module_std = pvsys.Pmp / nom_modules_total

# for n in range(num_strings_with_missing_modules):
#     for m in range(num_missing_modules):
#         del pvsys.pvstrs[n].pvmods[0] # Removing first module in string
#         # pvsys.setSuns({n: {m: 0.}})
#     # pvsys.pvstrs[n].pvmods = pvsys.pvstrs[n].pvmods[num_missing_modules:]

# pvsys.update()

# #dividing on standard array length to get power of the full string length
# power_per_module_degraded = pvsys.Pmp / nom_modules_total

# print(f'{power_per_module_std=}')
# print(f'{power_per_module_degraded=}')

# module_eq_diff = (power_per_module_std - power_per_module_degraded) * nom_modules_total / power_per_module_std

# Pnom_reduction = num_strings_with_missing_modules*num_missing_modules

# print(f'{Pnom_reduction=}')
# print(f'{module_eq_diff=}')
# print(f'Mismatch = {module_eq_diff/Pnom_reduction - 1}')
