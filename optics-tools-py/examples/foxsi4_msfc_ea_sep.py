"""
Make and save a single plot of an optic effective area.
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks

from optics_tools_py.io import mca
from optics_tools_py.ea import analysis

source_data = {
    "FM1": { # files for optic module FM1:
        'bg': '../data/fm1/20230711_FOXSI4_FM1_Effective_Area_OFOptic_Ti_NoFilter_25d0kV_0d35mA_3600sec.mca',
        'op': [
            '../data/fm1/20230711_FOXSI4_FM1_Effective_Area_withOptic_Ti_NoFilter_25d0kV_0d35mA_OnAxis_Focused_1200sec.mca'
        ],
        'material': 'Ti' # the window material used (you get these lines in the observed spectrum)
    },
    "FM2": { # files for optic module FM1:
        # these are low-energy data
        'bg': '../data/fm2/20230604_FOXSI_FM2_effective_area_25.05kV0d30mA_NO_OPTIC__1200sec.mca',
        'op': [
            '../data/fm2/20230604_FOXSI_FM2_effective_area_25.05kV0d30mA_BEAM_ON_OPTIC_onaxis_Pp0_Tn1__1200sec.mca',
            '../data/fm2/20230607_FOXSI_FM2_wCollimator_effective_area_Fe_25.05kV0d30mA_BEAM_ON_OPTIC_onaxis_Pp0_Tp0__1200sec.mca'
        ],
        # these are high energy data
        # 'bg': '../data/fm2/20230607_FOXSI_FM2_wCollimator_effective_area_Fe_25.05kV0d30mA_NO_OPTIC__1200sec.mca',
        # 'op': [
        #     '../data/fm2/20230607_FOXSI_FM2_wCollimator_effective_area_Fe_25.05kV0d30mA_BEAM_ON_OPTIC_onaxis_Pp0_Tp0__1200sec.mca'
        # ],
        'material': 'Fe' # the window material used (you get these lines in the observed spectrum)
    },
    "FM3": { # files for optic module FM1:
        'bg': '../data/fm3/20230712_FOXSI4_FM3_Effective_Area_IncidentFlux_Ti_NoFilter_25d0kV_0d35mA_3600sec.mca',
        'op': [
            '../data/fm3/20230712_FOXSI4_FM3_Effective_Area_withOptic_Ti_NoFilter_25d0kV_0d35mA_Aligned_X18d425_Y15d550_Pn2arcmin_Tn2_300sec.mca',
            '../data/fm3/20230712_FOXSI4_FM3_Effective_Area_withOptic_Ti_NoFilter_25d0kV_0d35mA_Aligned_X18d425_Y15d550_Pn2arcmin_Tn2_1200sec.mca', 
            '../data/fm3/20230712_FOXSI4_FM3_Effective_Area_withOptic_Ti_NoFilter_25d0kV_0d35mA_X18d425_Y15d550_Aligned_Pn1arcmin_Tn6_1200sec.mca'
        ],
        'material': 'Ti' # the window material used (you get these lines in the observed spectrum)
    }
}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("use like this:\n\t> python foxsi4_msfc_ea.py path/to/save.pdf")
        sys.exit()
    
    # data = analysis.make_ea(sys.argv[1], sys.argv[2], analysis.ti_lines)

    # choose an optic to make an EA plot for:
    optic = 'FM1'

    fig = plt.figure(figsize=(4,3))
    raw = source_data[optic]['op'][0]
    data = analysis.make_ea(source_data[optic]['bg'], source_data[optic]['op'][0], source_data[optic]['material'])

    ax = fig.add_subplot(1,1,1)
    ax.scatter(data['bg']['bins'], data['ea']*100*100, s=1, color='black')
    ax.grid(visible=True)
    ax.set_xlabel('Energy [keV]')
    ax.set_ylabel('Area [cm^2]')
    ax.set_xlim([5,20])
    ax.set_title(label="FM1 optic effective area")

    plt.tight_layout()
    outpath = Path(sys.argv[1]) / (optic + "_ea" + ".pdf")
    plt.savefig(outpath, dpi=400)
    plt.show()

