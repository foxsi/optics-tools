import os, pathlib
import re

def load_mca(path):
    """
    Load an Amptek .mca file as a `str`.

    Parameters
    ----------
        path: path to the file
    
    Returns
    -------
        the file content as a `str`.
    """
    if not path.endswith('.mca'):
        raise "bad extension"
    with open(path, 'r', errors='ignore') as data:
        value = data.read()
        return value

def stringbetween(source:str, start:str, stop:str):
    """
    Return the string data between a stop and start token.
    """
    matches = re.findall(start + '(.+?)' + stop, source, re.DOTALL)
    blob = ''
    for s in matches:
        blob += s
    return blob

def mca_to_structure(path):
    """
    Get a `dict` containing some blocks of data from an Amptek .mca file.

    Parameters
    ----------
        path: a path to the .mca file.
    
    Returns
    -------
        a `dict` containing `str` keys: 
            - `data`: a list of the raw ADC values (as `int`s)
            - `livetime`: a `float` value for the detector's livetime
            - `calibration_adc`: the calibration values of some ADC bins
            - `calibration_energy`: the calibrated energy values corresponding to `calibration_adc`.
    """
    rawmca = load_mca(path)
    
    # start and stop tokens for ADC data list
    data_start_key = '<<DATA>>'
    data_stop_key = '<<END>>'

    # NIHARIKA's TIP: USE `REAL_TIME` INSTEAD for the live time value:
    # livetime_key = "LIVE_TIME - "
    livetime_key = "REAL_TIME - "

    # start and stop tokens for the calibration data list
    calibration_start_key = '<<CALIBRATION>>'
    calibration_stop_key = '<<ROI>>'

    # pull out raw ADC data as `list[int]`
    datastr = stringbetween(rawmca, data_start_key, data_stop_key)
    data = [int(x) for x in datastr.split('\n') if x.isdigit()]

    # pull out livetime as `float`
    livetimestr = stringbetween(rawmca, livetime_key, "\n")
    livetime = float(livetimestr)

    # pull out calibration data as a list of `adcs` and `energies`.
    calibrationstr = stringbetween(rawmca, calibration_start_key, calibration_stop_key)
    caliblines = [s for s in calibrationstr.split('\n')]
    adcs = []
    energies = []
    for line in caliblines:
        try:
            lr = line.split(' ')
            if len(lr) == 2:
                adcs.append(float(lr[0]))
                energies.append(float(lr[1]))
        except:
            continue

    dp5_config_start_key = '<<DP5 CONFIGURATION>>'
    dp5_config_stop_key = '<<DP5 CONFIGURATION END>>'

    output = {
        'data':                 data,
        'livetime':             livetime,
        'calibration_adc':      adcs,
        'calibration_energy':   energies,
    }
    return output