import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import TFR_Analysis as TFR

sex_ratio = 1.055

df_dtypes = {"ARDY": float}

#na_values = ["."]

df = pd.read_csv("Poland_ASFR.csv", dtype = df_dtypes, na_values = {'ARDY': ["12-", "55+"]});


df.dropna(inplace = True)
df["Cohort"] = df["Cohort"].astype(float)

for obs_year in [2002, 2006, 2010, 2014]:

    merged_data = TFR.Backtesting('ASFR', df, obs_years = [obs_year])

    md = lambda y: merged_data[merged_data['Cohort'] == y]

    plot_asfr_errors = lambda y: plt.plot(md(y)['ARDY'], md(y)['ASFR_extrapolated'] - md(y)['ASFR_observed'])


    plt.figure(obs_year)
    for cutoff in [34, 36, 38, 40, 42]:
        plot_asfr_errors(obs_year - cutoff)


plt.show()
