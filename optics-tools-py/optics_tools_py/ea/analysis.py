import numpy as np
from scipy.signal import find_peaks

from optics_tools_py.io import mca

# line energies for Ti, Mo, and Fe.
ti_lines = [4.51, 4.93]
mo_lines = [(17.37 + 17.48)/2, 19.61]
fe_lines = [6.39, 7.06]


# the size of the pinhole or detector that is being illuminated:
AREA_PINHOLE = 25/1000/1000

# finite distance source correction factor:
FINITE_SOURCE_CORRECTION = 1/0.9218

# THIS VALUE GETS CALIBRATION DATA TO LINE UP WITH WAYNE'S MODEL, BUT IT IS PURELY FUDGED!
# AREA_PINHOLE = 48/1000/1000

def calibrate_from(file:str, other:dict):
    """
    Apply the energy calibration from another file (fit stored in `other['calibration']`) to this file's data.
    """
    # apply `other`'s calibration to this data to convert ADC bins
    data = mca.mca_to_structure(file)
    counts = np.array(data['data'])
    livetime = np.array(data['livetime'])
    # counts = counts/np.max(counts)
    fit = other['calibration']
    ebins = np.linspace(0,fit(len(counts)),len(counts))

    fluxes = counts / livetime

    return {"bins":ebins, "counts":counts, "flux":fluxes, "calibration":fit}

def calibrate(file:str, source_lines):
    """
    Calibrate a .mca file by linear fit of ADC peaks to the provided `source_lines` energy valies.
    """
    data = mca.mca_to_structure(file)
    counts = np.array(data['data'])
    livetime = np.array(data['livetime'])
    # counts = counts/np.max(counts)
    
    nlines = len(source_lines)
    
    caps = []
    diff = np.diff(counts)

    # identify peak locations as zero-crossings of derivative
    for i in range(len(counts) - 2):
        if diff[i] > 0 and diff[i+1] < 0:
            caps.append(i+1)
    
    caps = np.array(caps) # convert list to np array for other operations
    peak_counts = counts[caps] # get number of counts at each cap location

    ind = peak_counts.argsort()
    ind = ind[::-1] # reverse the array, argsort is min to max by default.
    lineADC = caps[ind[0:nlines]] # ADC value of each major emission line

    fit = np.polynomial.polynomial.Polynomial.fit(lineADC, source_lines, 1)

    # fit = np.polynomial.polynomial.Polynomial.fit(data['calibration_adc'], data['calibration_energy'], 1)
    print("fit line:", fit)
    ebins = np.linspace(0,fit(len(counts)),len(counts))

    fluxes = counts / livetime

    return {"bins":ebins, "counts":counts, "flux":fluxes, "calibration":fit}

def make_ea(bgfile:str, opticfile:str, source_lines):
    """
    Calculate effective area curve for the optic data provided.

    Parameters
    ----------
        bgfile: an Amptek .mca file containing background measurement, without the optic.

        opticfile: an Amptek .mca file containing data with the optic present.

        source_lines: a string or list. If a list, should contain energy values of emission lines. If a string, should be an element name 'Ti' or 'Fe'.

    Returns
    -------
        a `dict[str]` containing:
            - 'bg': the calibrated background 
    """
    source = []
    if type(source_lines) is str:
        if source_lines == 'Ti':
            source = ti_lines
        elif source_lines == 'Fe':
            source = fe_lines
        else:
            raise "Undefined window material"
    elif type(source_lines) is list:
        source = source_lines
    else:
        raise "Undefined window material"
    bg = calibrate(bgfile, source)
    op = calibrate_from(opticfile, bg)
    
    if len(bg["bins"]) != len(op["bins"]):
        raise "background and with-optic data must have same number of energy bins!"
    
    # will divide by bg flux: so replace zeros in that array with NaN
    bg['flux'][bg['flux'] ==  0] = np.nan

    # calculate the effective area curve:
    ea = FINITE_SOURCE_CORRECTION*AREA_PINHOLE*op["flux"]/bg["flux"]

    result = {"bg": bg, "op": op, "ea": ea}

    return result