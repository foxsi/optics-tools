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

colors = ['red', 'green', 'blue']

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("use like this:\n\t> python foxsi4_msfc_ea.py path/to/save.pdf")
        sys.exit()
    
    nopt = 3    # number of optics modules in `source_data` (rows)
    nplot = 3   # number of plots to make per module (cols)
    
    fig = plt.figure(figsize=(10,8))

    for k, key in enumerate(source_data.keys()): # loop over optics
        bg = source_data[key]['bg']
        ops = source_data[key]['op']

        # get the effective area (ea) for this optic's background 
        data = analysis.make_ea(bg, source_data[key]['op'][0], source_data[key]['material'])
        
        # check how many files to plot for this optic (how many measurements were taken)
        nfile = len(source_data[key]['op'])
            
        print(key, k)
        pk = k+1
        bg_ax = fig.add_subplot(nopt, nplot, 1 + 3*k)
        op_ax = fig.add_subplot(nopt, nplot, 2 + 3*k, sharex=bg_ax)
        ea_ax = fig.add_subplot(nopt, nplot, 3 + 3*k, sharex=bg_ax)
        op_e_ax = op_ax.twiny()
        ea_e_ax = ea_ax.twiny()

        bg_ax.plot(data['bg']['counts'], color='black')
        bg_ax.set_xlabel('ADC')
        bg_ax.set_ylabel(key + '\n' + 'Counts')
        # bg_ax.grid(visible=True)
        # adc_ax.set_yscale('log')

        bg_e_ax = bg_ax.twiny()
        bg_e_ax.set_xlim([0, np.max(data['bg']['bins'])])
        bg_e_ax.set_xlabel('Energy [keV]')
        bg_e_ax.grid(visible=True)
        bg_ax.set_title(label="Without optic")

        for i in range(len(ops)):
            thisdata = analysis.make_ea(bg, ops[i], source_data[key]['material'])
            op_ax.plot(thisdata['op']['counts'], color=colors[i])
            ea_ax.scatter(np.arange(0,len(thisdata['ea'])), thisdata['ea']*100*100, s=1, color=colors[i])

        op_ax.set_xlabel('ADC')
        op_ax.set_ylabel('Counts')
        # bg_ax.scatter(data['bg'], counts[lineADC], s=100, marker='+', color='k')
        # adc_ax.set_yscale('log')
        
        op_e_ax.set_xlim([0, np.max(data['op']['bins'])])
        op_e_ax.set_xlabel('Energy [keV]')
        op_e_ax.grid(visible=True)
        op_ax.set_title(label="With optic")
        
        ea_ax.set_xlabel('ADC')
        ea_ax.set_ylabel('Area [cm^2]')
        # ea_ax.grid(visible=True)
        # bg_ax.scatter(data['bg'], counts[lineADC], s=100, marker='+', color='k')
        # ea_ax.set_yscale('log')
        
        ea_e_ax.set_xlim([0, np.max(data['op']['bins'])])
        ea_e_ax.set_xlabel('Energy [keV]')
        ea_e_ax.grid(visible=True)
        ea_ax.set_title(label="Effective area")

        if key == 'FM2':
            ea_ax.legend(['No collimator', 'Collimator'], fontsize=8)

    # e_ax.grid(visible=True)

    # plotting differences for peak finding:
    # diff_ax = fig.add_subplot(1,2,2)
    # diff_ax.plot(np.diff(counts), 'k')
    # diff_ax.scatter(np.arange(len(np.diff(counts))),np.diff(counts), marker='.', color='k')
    # plt.axhline(y=0, color='red')

    plt.tight_layout()
    outpath = Path(sys.argv[1]) / ("result" + ".pdf")
    plt.savefig(outpath, dpi=400)
    plt.show()