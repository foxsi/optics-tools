import sys, time
from pathlib import Path
# from foxsi_optics_calib.ccd.ccd import AndorCCDImage, AndorCCDPsfImage, AndorCCDPsfFitImage, CCDFitImage
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm

import scipy.optimize as opt
import numpy as np
from astropy.io import fits as pyfits
from astropy.modeling.fitting import LevMarLSQFitter, TRFLSQFitter, DogBoxLSQFitter
from astropy.modeling.models import Gaussian2D

fudge_factor = 1 #0.5 # 2324/2100
focal_length = 2
pixel_pitch = 11e-6
plate_scale_arcsec = np.arctan(pixel_pitch / focal_length) * 180/np.pi * 3600 * fudge_factor
sig2fwhm = 2*np.sqrt(2*np.log(2))

# 0 is the background, other numbers are the 
measurements = {
    # currently, no fm1 data in folder
    # 'fm1': {

    # }
    'fm2': {
        0: '/Users/thanasi/Documents/FOXSI/Optics/Calibration/data/fm2/PSF_Scan/20230623_Marana_FOXSI4_MMA_FM2_withCollimator_Calibration_Background_120Exp_0d5sEach_Focused_0Up_P0arcmin_T0arcmin_Z16d076_v2.fits',
        1: '/Users/thanasi/Documents/FOXSI/Optics/Calibration/data/fm2/PSF_Scan/20230623_Marana_FOXSI4_MMA_FM2_withCollimator_Calibration_Ti_NoFilter_12d78kV_0.78mA_120Exp_0d5sEach_Focused_0Up_P0d0_T0d0_Z16d076.fits',
        2: '/Users/thanasi/Documents/FOXSI/Optics/Calibration/data/fm2/PSF_Scan/20230623_Marana_FOXSI4_MMA_FM2_withCollimator_Calibration_Ti_NoFilter_12d78kV_0.78mA_120Exp_0d5sEach_Focused_0Up_P0arcmin_T0arcmin_Z16d076_v2.fits'
    },
    'fm3': {
        0: '/Users/thanasi/Documents/FOXSI/Optics/Calibration/data/fm3/20230621_Marana_FOXSI4_MMA_FM3_Calibration_Background_960Exp_0d5sEach_aligned_focused__260Up.fits',
        1: '/Users/thanasi/Documents/FOXSI/Optics/Calibration/data/fm3/20230621_Marana_FOXSI4_MMA_FM3_Calibration_Ti_12d78kV_0d24mA_NoFilter_960Exp_0d5sEach_aligned_focused_Pn1_Tpn1_Fp15d81_260Up.fits'
    }
}

def gauss2d(data, A, x0, y0, s_x, s_y, ang, offset):
    x = data[0]
    y = data[1]
    a = np.cos(ang)**2 / 2 / s_x**2 + np.sin(ang)**2 / 2 / s_y**2
    # b = -np.sin(ang)*np.cos(ang) / 2 / s_x**2 + np.sin(ang)*np.cos(ang) / 2 / s_y**2
    b = np.sin(2*ang) / 4 / s_x**2 - np.sin(2*ang)*np.cos(ang) / 4 / s_y**2
    c = np.sin(ang)**2 / 2 / s_x**2 + np.cos(ang)**2 / 2 / s_y**2
    # f = offset + A*np.exp(-(a*(x - x0)**2 + 2*b*(x - x0)*(y - y0) + c*(y - y0)**2))
    f = A*np.exp(-(a*(x - x0)**2 + 2*b*(x - x0)*(y - y0) + c*(y - y0)**2))
    return f.ravel()

def fit_bisect_gauss2d(x, y, z, init=None):
    y_peak, x_peak = np.unravel_index(data.argmax(), data.shape)

    a_scale = 1e-1
    stddev_lo_tol = 1e-6
    stddev_hi_tol = 100
    base_bound = {
        'amplitude': (1e-6, np.inf),
        'x_mean':    (x_peak - a_scale, x_peak + a_scale),
        'y_mean':    (y_peak - a_scale, y_peak + a_scale),
        'x_stddev':  (stddev_lo_tol, stddev_hi_tol),
        'y_stddev':  (stddev_lo_tol, stddev_hi_tol),
        'theta':     (0, 2*np.pi)
    }

    g_base = Gaussian2D(
        amplitude=1,
        x_mean=   x_peak,
        y_mean=   y_peak,
        x_stddev=(stddev_lo_tol+stddev_hi_tol)/2,
        y_stddev=(stddev_lo_tol+stddev_hi_tol)/4,
        theta=    0,
        bounds=   base_bound
    )
    fit = TRFLSQFitter()
    if init is None:
        g_opt = fit(g_base, x.ravel(), y.ravel(), z.ravel(), maxiter=10000)
        return g_opt
    if type(init) is Gaussian2D:
        init = [init]
    
    outs = []
    for i, g in enumerate(init):
        # bisect as initial condition, form bounds, and do fittings.

        lo_bound = base_bound.copy()
        hi_bound = base_bound.copy()
        lo_bound['x_stddev'] = (stddev_lo_tol, g.x_stddev.value)
        lo_bound['y_stddev'] = (stddev_lo_tol, g.y_stddev.value)
        hi_bound['x_stddev'] = (g.x_stddev.value, stddev_hi_tol)
        hi_bound['y_stddev'] = (g.y_stddev.value, stddev_hi_tol)
        g_lo = Gaussian2D(
            amplitude=1,
            x_mean=   x_peak,
            y_mean=   y_peak,
            x_stddev=(lo_bound['x_stddev'][0] + lo_bound['x_stddev'][1])/2,
            y_stddev=(lo_bound['y_stddev'][0] + lo_bound['y_stddev'][1])/2,
            theta=    0,
            bounds=   lo_bound
        )
        g_hi = Gaussian2D(
            amplitude=1,
            x_mean=   x_peak,
            y_mean=   y_peak,
            x_stddev=(hi_bound['x_stddev'][0] + hi_bound['x_stddev'][1])/2,
            y_stddev=(hi_bound['y_stddev'][0] + hi_bound['y_stddev'][1])/2,
            theta=    0,
            bounds=   hi_bound
        )
        
        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("use like this:\n\t> python3 foxsi4_msfc_1gauss.py path/to/plot/save/folder/")
        sys.exit()
    print("saving to", sys.argv[1])
    
    for key in measurements.keys():
        for subkey in measurements[key].keys():
            if subkey == 0:
                continue
            
            f = measurements[key][subkey]
            d = measurements[key][0]

            fits = pyfits.open(f)
            darks = pyfits.open(d)
            if len(fits[0].data.shape) == 3:
                print("Found {0} exposures. Averaging...".format(
                    fits[0].data.shape[0]))
                data = np.average(fits[0].data, axis=0) - np.average(darks[0].data, axis=0)
            else:
                data = fits[0].data - darks[0].data
            
            # scale to arcsec:
            # data = data*plate_scale_arcsec
            data = data/data.max()
            # everything below here in arcsec now!!
            
            x, y = np.meshgrid(*[np.arange(v) for v in data.shape])# * u.pixel
            # x *= plate_scale_arcsec
            # y *= plate_scale_arcsec
            arcsec_ticks = np.arange(0,2048)*plate_scale_arcsec

            print("x:")
            print("\tshape:", x.shape)
            print("\trange:", np.ptp(x))

            # x_r, y_r = np.meshgrid(data)

            # x_r  = data.ravel(order='C')
            # y_r  = data.ravel(order='F')
            # # x_r = data[x].reshape(1,-1)
            # # y_r = data[y].reshape(1,-1)

            # data_form = np.stack((x_r, y_r), axis=0)

            # do fitting:
            # x_peak = np.max(np.max(data, axis=0))
            # y_peak = np.max(np.max(data, axis=1))
            y_peak, x_peak = np.unravel_index(data.argmax(), data.shape)

            print("peak:", x_peak, y_peak)
            
            guess = (np.max(data.ravel()), x_peak, y_peak, 1, 1, 0,0)
            bound_basic = (
                [-np.inf,   -np.inf,    -np.inf,  0,       0,     -np.pi/2, -np.inf],
                [np.inf,     np.inf,     np.inf,  np.inf,  np.inf, np.pi/2, np.inf]
            )
            bound_fix_peak = (
                [-np.inf, x_peak - 0.1, y_peak - 0.1, -np.inf, -np.inf, -np.pi, -np.inf],
                [np.inf, x_peak + 0.1, y_peak + 0.1, np.inf, np.inf, np.pi, np.inf]
            )

            bound_fix_amp = (
                [data.max() - 0.1, x_peak - 0.1, y_peak - 0.1, -np.inf, -np.inf, -np.pi, -np.inf],
                [data.max() + 0.1, x_peak + 0.1, y_peak + 0.1, np.inf, np.inf, np.pi, np.inf]
            )
            start_opt = time.time()
            # popt, pcov = opt.curve_fit(gauss2d, (x, y), data.ravel(), p0=guess, bounds=bound_fix_peak)
            # popt, pcov = opt.curve_fit(gauss2d, (x, y), data.ravel(), p0=guess, bounds=bound_fix_amp)

            a_scale = 1e-1
            stddev_lo_tol = 1e-6
            stddev_hi_tol = 100
            bounds1 = {
                'amplitude': (1e-6, np.inf),
                'x_mean': (x_peak - a_scale, x_peak + a_scale),
                'y_mean': (y_peak - a_scale, y_peak + a_scale),
                'x_stddev': (stddev_lo_tol, stddev_hi_tol),
                'y_stddev': (stddev_lo_tol, stddev_hi_tol),
                'theta': (0, 2*np.pi)
            }
            print("fitting...")
            g_init1 = Gaussian2D(
                amplitude=1,
                x_mean=x_peak,
                y_mean=y_peak,
                x_stddev=(stddev_lo_tol+stddev_hi_tol)/2,
                y_stddev=(stddev_lo_tol+stddev_hi_tol)/4,
                theta=0,
                bounds=bounds1
            )
            fit = TRFLSQFitter()
            g_opt1 = fit(g_init1, x.ravel(), y.ravel(), data.ravel(), maxiter=10000)

            duration = time.time() - start_opt
            print("solved in", duration, "seconds")

            print("opt params:", g_opt1)
            amp     = g_opt1.amplitude.value
            x_mean  = g_opt1.x_mean.value
            y_mean  = g_opt1.y_mean.value
            x_sig   = g_opt1.x_stddev.value
            y_sig   = g_opt1.y_stddev.value
            ang     = g_opt1.theta.value
            # amp, x_mean, y_mean, x_sig, y_sig, ang, offset = g_opt1
            # optimizer doesn't care about our conventions for major/minor axis:
            x_sig = np.max([x_sig, y_sig])
            y_sig = np.min([x_sig, y_sig])
            x_fwhm = x_sig*sig2fwhm
            y_fwhm = y_sig*sig2fwhm

            print("fwhms:", x_fwhm, y_fwhm)
            
            ang_correct = np.pi/4
            # ang = ang + ang_correct
            maj_fwhm = [x_fwhm*np.cos(ang), x_fwhm*np.sin(ang)]
            min_fwhm = [y_fwhm*np.cos(ang+np.pi/2), y_fwhm*np.sin(ang+np.pi/2)]

            # coord     axis
            # x         maj     min
            # y         maj     min
            x_plot_fwhm = np.array([np.cos(ang), y_fwhm/x_fwhm*np.cos(ang + np.pi/2)])
            y_plot_fwhm = np.array([np.sin(ang), y_fwhm/x_fwhm*np.sin(ang + np.pi/2)])

            # Evaluate the fit function on the basis:
            # res_fit = gauss2d((x, y), *popt)
            res_fit = g_init1.evaluate(x, y, amp, x_mean, y_mean, x_sig, y_sig, ang)
            res_fit = res_fit.reshape(data.shape)
            
            nplotr = 2
            nplotc = 2
            fig = plt.figure(figsize=(10,8))
            raw_ax = fig.add_subplot(nplotr, nplotc, 1)
            imshow = raw_ax.imshow(data, origin='lower', #vmin=vmin, vmax=vmax,
                           cmap=plt.cm.viridis)
            plt.title(label="BG-subtracted image")
            # raw_ax.grid(color='white', ls='solid', alpha=0.5)
            raw_ax.set_xlabel('X [arcsec]')
            raw_ax.set_ylabel('Y [arcsec]')
            raw_ax.set_xticks([arcsec_ticks[0], arcsec_ticks[-1]])
            raw_ax.set_yticks([arcsec_ticks[0], arcsec_ticks[-1]])
            plt.setp(raw_ax.get_xticklabels(), rotation=90, horizontalalignment='center')

            a_side = 20 # arcsec halfbox
            xlims_i = np.array([int(np.floor(x_mean - a_side)), int(np.ceil(x_mean + a_side))])
            ylims_i = np.array([int(np.floor(y_mean - a_side)), int(np.ceil(y_mean + a_side))])
            xlims_arcsec = np.floor(xlims_i*plate_scale_arcsec).astype(int)
            ylims_arcsec = np.floor(ylims_i*plate_scale_arcsec).astype(int)

            fit_ax = fig.add_subplot(nplotr, nplotc, 2)
            imshow_fit = fit_ax.imshow(data, origin='lower', #vmin=vmin, vmax=vmax,
                           cmap=plt.cm.viridis)
            fit_ax.set_title("PSF detail")

            scat_mean = fit_ax.scatter(x_mean, y_mean, color="magenta")
            scat_mode = fit_ax.scatter(x_peak, y_peak, color="black", marker="+")
            levels=np.array([0.1, 1, 20, 30, 50, 75])
            cont_raw = fit_ax.contour(data, levels=levels/100, colors="white")
            cont_meas = fit_ax.contour(res_fit, levels=levels/100, colors="grey")
            fig.colorbar(imshow_fit, ax=fit_ax)
            plt.setp(fit_ax.get_xticklabels(), rotation=90, horizontalalignment='right')
            plt.xlim(xlims_i)
            plt.ylim(ylims_i)
            fit_ax.set_xticks(xlims_i, xlims_arcsec)
            fit_ax.set_yticks(ylims_i, ylims_arcsec)
            fit_ax.set_xlabel('X [arcsec]')
            fit_ax.set_ylabel('Y [arcsec]')
            # fig.colorbar(fit_ax.pcolormesh(data), ax=fit_ax)

            
            res_ax = fig.add_subplot(nplotr, nplotc, 4)
            res_meas =        data[ylims_i[0]:ylims_i[1], xlims_i[0]:xlims_i[1]]
            res_fit_zoom = res_fit[ylims_i[0]:ylims_i[1], xlims_i[0]:xlims_i[1]]

            residual = res_meas - res_fit_zoom
            res_ax.imshow(residual, origin='lower', cmap=plt.cm.viridis)
            res_ax.set_title("Residual")
            plt.setp(res_ax.get_xticklabels(), rotation=90, horizontalalignment='right')
            res_ax.set_xlabel('X [arcsec]')
            res_ax.set_ylabel('Y [arcsec]')
            res_ax.set_xticks(xlims_arcsec)
            res_ax.set_yticks(ylims_arcsec)
            fig.colorbar(res_ax.pcolormesh(residual), ax=res_ax)

            print_ax = fig.add_subplot(nplotr, nplotc, 3)
            display_txt = "FWHM:        ({:.2f}, {:.2f}) arcsec".format(x_fwhm*plate_scale_arcsec, y_fwhm*plate_scale_arcsec)
            display_txt += "\nRMS FWHM:     {:.2f} arcsec".format(np.sqrt(x_fwhm**2 + y_fwhm**2)*plate_scale_arcsec)
            display_txt += "\neccentricity: {:.2f}".format(np.sqrt(1 - y_fwhm**2 / x_fwhm**2))
            display_txt += "\nangle:        {:.2f} deg".format(ang*180/np.pi)
            print_ax.text(0,0,display_txt, horizontalalignment='left', verticalalignment='center', fontfamily='monospace')
            print_ax.set_xlim((0,2))
            print_ax.set_ylim((-1,1))
            # print_ax.set_ylim((-1,1))
            print_ax.set_axis_off()
            
            plt.tight_layout()

            this_name = key.upper() + "_scan" + str(subkey)
            outpath = Path(sys.argv[1]) / (this_name + ".pdf")
            # plt.savefig(outpath, dpi=400)
            plt.savefig(outpath)
            plt.show()