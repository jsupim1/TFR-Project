import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import TFR_Analysis as TFR
import Model_ASFR

# Add plotting of fitted ASFR profiles year by year

##[res, ax] = TFR.Fit_ASFR(1978, [15, 35], 1)
##TFR.Plot_by_cohort([1978], ax)
##plt.show()
##
##fig = plt.figure()
##
##[res, ax] = TFR.Fit_ASFR(1979, [15, 35], 1)
##TFR.Plot_by_cohort([1979], ax)
##plt.show()
##
##fig = plt.figure()
##
##
##[res, ax] = TFR.Fit_ASFR(1980, [15, 35], 1)
##TFR.Plot_by_cohort([1980], ax)
##plt.show()
mean_cost = 0

for c in range(1956, 1987, 5):
    res = TFR.Fit_ASFR(c, [15, 40], 0)
    sns.lineplot(data = df[df["Cohort"] == c], x = "ARDY", y = "ASFR", label = "Cohort (obs): " + str(c))


    x_all = np.linspace(12, 55, 44); # Extrapolation starts 1 year after the cutoff
    y_all = res.x[0]*np.array(Model_ASFR.ASFR_function(res.x[1:], x_all ))

    sns.lineplot(x = x_all, y = y_all, label = "Cohort " + str(c), linestyle='--')
    
    #print(res.x[1:4])
    #print(res.cost)

    mean_cost += res.cost

plt.show()
mean_cost = mean_cost / (1987-1956)

print(mean_cost)
