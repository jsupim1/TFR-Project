import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from astropy import modeling

from matplotlib.widgets import Button, Slider


def Distorted_Gaussian(Parameters, X):

    sigma1, sigma2, mu = Parameters

    sigma1 = abs(sigma1) + 10**(-8)
    sigma2 = abs(sigma2) + 10**(-8)

    power = np.array([ -0.5*((x - mu)/sigma1)**2 if x < mu else -0.5*((x - mu)/sigma2)**2 for x in X])

    f = (1/np.sqrt(2*np.pi)) * (2/(sigma1 + sigma2)) * np.exp(power)

    return list(f)


def Two_Gaussians(Parameters, X):

    c_early, sigma1, sigma2, sigma_late, mu_early, mu_late = Parameters

    sigma1 = abs(sigma1) + 10**(-8)
    sigma2 = abs(sigma2) + 10**(-8)
    sigma_late = abs(sigma_late) + 10**(-8)

    exp1 = np.array([ np.exp(-0.5*((x - mu_early)/sigma1)**2) if x < mu_early else np.exp(-0.5*((x - mu_early)/sigma2)**2) for x in X])
    exp2 = np.array([ np.exp(-0.5*((x - mu_late)/sigma_late)**2) for x in X])

    f = 2*(1/np.sqrt(2*np.pi)) * ( (2*c_early/(sigma1+sigma2)) * exp1 + (1-c_early)/sigma_late * exp2 )

    return list(f)


def GompertzCDF(a, b, X):

    return [1-np.exp(-(np.exp(b*x) - 1)) for x in X]


def GompertzPDF(a, b, X):

    return [b*np.exp(1 + b*x - np.exp(b*x)) for x in X]


def GompertzGeneralized(alpha, beta, b, X):

    #print(GompertzCDF(a,b,X))

    Y = -np.log(-np.log(np.subtract(1,GompertzCDF(1,b,X))))

    Y = [alpha + beta*y for y in Y];

    G = [1-np.exp(- (np.exp(-alpha)*((np.exp(b*x) - 1))**beta )) for x in X]

    #print(G)

    return G

def GompertzGeneralizedPDF(Parameters, X):

    alpha, beta, b = Parameters

    #print(GompertzCDF(a,b,X))

    Y = -np.log(-np.log(np.subtract(1,GompertzCDF(1,b,X))))

    Y = [alpha + beta*y for y in Y];

    G = [1-np.exp(- (np.exp(-alpha)*((np.exp(b*x) - 1))**beta )) for x in X]

    #G = [1-np.exp(-np.exp(-y)) for y in Y]

    G_pdf = [(G[i+1] - G[i])/(X[i+1] - X[i]) for i in range(0, len(X) - 1)]

    #print(G)

    return G_pdf
##
##x = list(range(12, 70))
##fig, ax = plt.subplots()
##line, = ax.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0, 1, 0.1, x))
###ax.plot(x, [np.exp(2.5)*0.05*2*np.exp(-(1+2)*0.05*z ) * 1/(1-(1+2)*np.exp(-0.05*z)) for z in x])
##
##axalpha = fig.add_axes([0.25, 0.1, 0.65, 0.03])
##alpha_slider = Slider(
##    ax=axalpha,
##    label='alpha',
##    valmin=-1,
##    valmax=10,
##    valinit=1,
##)
##axbeta = fig.add_axes([0.25, 0.05, 0.65, 0.03])
##beta_slider = Slider(
##    ax=axbeta,
##    label='beta',
##    valmin=0.1,
##    valmax=10,
##    valinit=1,
##)
##axb = fig.add_axes([0.25, 0.15, 0.65, 0.03])
##b_slider = Slider(
##    ax=axb,
##    label='b',
##    valmin=0.002,
##    valmax=0.2,
##    valinit=0.05,
##)
##
##
##def update(val):
##    line.set_ydata(GompertzGeneralizedPDF(alpha_slider.val, beta_slider.val, b_slider.val, x))
##    fig.canvas.draw_idle()


# register the update function with each slider
##alpha_slider.on_changed(update)
##beta_slider.on_changed(update)
##b_slider.on_changed(update)
####plt.plot(x, GompertzPDF(0.2, 0.1, [xi for xi in x]))
####plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.1, 1, 0.2, 0.1, x))
####plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.25, 1, 0.2, 0.1, x))
####plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(0.5, 1, 0.2, 0.1, x))
####plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(1, 1, 0.2, 0.1, x))
####plt.plot([(c + d)/2 for c, d in zip(x[1:], x[:-1])], GompertzGeneralizedPDF(3, 2, 0.2, 0.1, x))
##plt.show()

