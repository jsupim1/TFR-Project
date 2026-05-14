import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from astropy import modeling

import Fertility_schedules
import TFR_Analysis

from matplotlib.widgets import Button, Slider

        
global fig
global line
global x

#def ASFR_function(delay, spread, B, x):
def ASFR_function(Parameters, x):

    #f = Fertility_schedules.GompertzGeneralizedPDF(Parameters, x)

    #f = Fertility_schedules.Distorted_Gaussian(Parameters, x)

    f = Fertility_schedules.Two_Gaussians(Parameters, x)

    return f

def update(val):
    global fig
    #line.set_ydata(ASFR_function(delay_slider.val, spread_slider.val, b_slider.val, x))
    line.set_ydata(ASFR_function([slider1.val, \
        slider2.val, slider3.val, slider4.val, slider5.val, slider6.val], \
                                x))
    fig.canvas.draw_idle()
    

def ASFR_function_plot(ax = []):

    global x
    global fig
    global line
    global slider1, slider2, slider3, slider4, slider5, slider6
    x = list(range(12, 70))
    if not ax:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    #line, = ax.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], ASFR_function(0, 1, 0.1, x))
    line, = ax.plot(x, ASFR_function([1, 1, 5, 5, 18, 30], x))

    #ax.plot(x, [np.exp(2.5)*0.05*2*np.exp(-(1+2)*0.05*z ) * 1/(1-(1+2)*np.exp(-0.05*z)) for z in x])

    ax1 = fig.add_axes([0.25, 0.05, 0.65, 0.03])
    slider1 = Slider(
        ax=ax1,
        label='c_e',
        valmin=0,
        valmax=1,
        valinit=1,
    )
    ax2 = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    slider2 = Slider(
        ax=ax2,
        label='sigma1',
        valmin=0.25,
        valmax=5,
        valinit=1,
    )
    ax3 = fig.add_axes([0.25, 0.15, 0.65, 0.03])
    slider3 = Slider(
        ax=ax3,
        label='sigma2',
        valmin=1,
        valmax=20,
        valinit=5,
    )
    ax4 = fig.add_axes([0.25, 0.2, 0.65, 0.03])
    slider4 = Slider(
        ax=ax4,
        label='sigma_late',
        valmin=1,
        valmax=20,
        valinit=5,
    )
    ax5 = fig.add_axes([0.25, 0.25, 0.65, 0.03])
    slider5 = Slider(
        ax=ax5,
        label='mu_early',
        valmin=12,
        valmax=70,
        valinit=18,
    )
    ax6 = fig.add_axes([0.25, 0.3, 0.65, 0.03])
    slider6 = Slider(
        ax=ax6,
        label='mu_late',
        valmin=12,
        valmax=70,
        valinit=30,
    )




    # register the update function with each slider
    slider1.on_changed(update)
    slider2.on_changed(update)
    slider3.on_changed(update)
    slider4.on_changed(update)
    slider5.on_changed(update)
    slider6.on_changed(update)

    plt.show(block = True)
    #z = input()

    return fig, ax
    ##plt.plot(x, GompertzPDF(0.2, 0.1, [xi for xi in x]))
    ##plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.1, 1, 0.2, 0.1, x))
    ##plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.25, 1, 0.2, 0.1, x))
    ##plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.5, 1, 0.2, 0.1, x))
    ##plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(1, 1, 0.2, 0.1, x))
    ##plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(3, 2, 0.2, 0.1, x))
    #plt.show()

