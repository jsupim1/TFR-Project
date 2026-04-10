import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from astropy import modeling

sex_ratio = 1.055

df_dtypes = {"ARDY": float}

#na_values = ["."]

df = pd.read_csv("Poland_ASFR.csv", dtype = df_dtypes, na_values = {'ARDY': ["12-", "55+"]});
fem = pd.read_csv("Poland_FemalePopulation.csv",
                  dtype = {'Exposure': float, 'Cohort': float, 'Age': float}, na_values = {'Exposure': ["."]});
deaths = pd.read_csv("Poland_DeathRates.csv",
                     dtype = {'Age': float, 'Female': float, 'Male': float, 'Total': float},
                     na_values = {'Age': ["110+"], 'Female': ['.'], 'Male': ['.'], 'Total': ['.']});
births = pd.read_csv("Poland_LiveBirths.csv",
                     dtype = {'Year': float, 'ARDY': float, 'Total': float},
                     na_values = {'ARDY': ["12-", "55+"]})


df.dropna(inplace = True)
fem.dropna(inplace = True)
deaths.dropna(inplace = True)
births.dropna(inplace = True)
#(fem[fem['Exposure'] == '.'].index, inplace=True)
#(deaths[deaths['Age'] == '110+'].index, inplace=True)
deaths.drop(deaths[deaths['Age'].astype(float) > 70].index, inplace=True)

df["Cohort"] = df["Cohort"].astype(float)
births["Cohort"] = births["Cohort"].astype(float)
#deaths["Age"] = deaths["Age"].astype(float)

deaths["Cohort"] = deaths["Year"] - deaths["Age"];

births_total = births.groupby('Year')["Total"].sum();

#print(df.head())
#print(fem.head(20))
#print(deaths.head())
#print(births.head(20))
#print(births_total.head(50))

def Plot_by_year(Years):

    for year in Years:
        sns.lineplot(data = df[df["Year"] == year], x = "ARDY", y = "ASFR", label = str(year))

    return 0

def Plot_by_cohort(Cohorts):

    for cohort in Cohorts:
        sns.lineplot(data = df[df["Cohort"] == cohort], x = "ARDY", y = "ASFR", label = str(cohort))

#Plot_by_cohort([1950, 1960, 1970, 1980, 1990, 2000])
#plt.show()

def Fit_Gaussian(cohort, cutoff_ages): # Fit a Gaussian function to ASFRs - this fitted Gaussian can be extrapolated beyond the late cutoff age
    
    df_cohort = df[df["Cohort"] == cohort] #Filter for cohort

    df_train = df_cohort[(df_cohort["ARDY"] >= cutoff_ages[0]) & (df_cohort["ARDY"] <= cutoff_ages[1])] # We only fit to ASFRs between the cutoff ages
    
    x_train = df_train["ARDY"]
    y_train = df_train["ASFR"]

    x_all = np.linspace(12, 55, 44);


    fitter = modeling.fitting.LevMarLSQFitter()
    model = modeling.models.Gaussian1D(amplitude = 0.1, mean = 25, stddev = 5)   # Initial values for the fitting algorithm to be revised
    fitted_model = fitter(model, x_train, y_train)

    
    #sns.lineplot(data = df_cohort, x = "ARDY", y = "ASFR")
    #sns.lineplot(x = x_all, y = fitted_model(x_all))
    #plt.show()

    return fitted_model # Returns a function

def Compute_births(year, fem, asfr): # We could modify this to take a series of years as argument

    fem_year = fem[fem["Cohort"] + fem["Age"] == year] # Filter women numbers for given year
    #print(fem_year)

    asfr = asfr[asfr["Year"] == year] # Filter ASFRs for given year
    #print(asfr)

    fem_year = fem_year.join(asfr.set_index("Cohort"), on = "Cohort", how = 'inner') # Join the two dataframes
    fem_year["Live_births"] = fem_year["Exposure"]*fem_year["ASFR"]
    #print(fem_year)

    births = sum(fem_year["Live_births"]) # Births in a given year are the sum of F_i*asfr_i, where i is the female age

    return births


def Extrapolate_ASFR(cohort, obs_year, asfr, ccf_only = 0, plot_flag = 0):
    
    fitted_model = Fit_Gaussian(cohort, [28, obs_year-cohort])

    x_extrapolated = np.linspace(min(obs_year-cohort+1, 55), 55, max(0, 55 - (obs_year-cohort))); # Extrapolation starts 1 year after the cutoff
    y_extrapolated = fitted_model(x_extrapolated);
    
    asfr_cohort_observed = asfr[(asfr["ARDY"] <= obs_year - cohort) & (asfr["Cohort"] == cohort)]; # Filter for ages, and filter for the analysed cohort
    #print(asfr_cohort_observed)
    if len(y_extrapolated) == 0:
        extrapolated_flag = 0
    else:
        extrapolated_flag = 1

    if ccf_only:
        CCF = sum(asfr_cohort_observed["ASFR"]) + sum(y_extrapolated);

        #print(CCF)
    
        if plot_flag:
            sns.lineplot(x = x_extrapolated, y = fitted_model(x_extrapolated), label = str(obs_year))
    

        return [CCF, extrapolated_flag]

    else:
        asfr_extrapolated = pd.DataFrame([ [i, j, 1] for i, j in zip(x_extrapolated, y_extrapolated)], columns = ["ARDY", "ASFR", "Extrapolated?"])

        asfr_extrapolated['Year'] = cohort + asfr_extrapolated['ARDY']
        asfr_extrapolated['Cohort'] = cohort

        print(asfr_extrapolated)
        
        return asfr_extrapolated


    return 0
    

##def Extrapolate_CCF(cohort, obs_year, asfr, plot_flag = 0):
##
##    fitted_model = Fit_Gaussian(cohort, [28, obs_year-cohort]) # Fit a Gaussian to observed ASFRs, based on ASFRs observed in ages between [X, Y]
##
##    x_extrapolated = np.linspace(min(obs_year-cohort+1, 55), 55, max(0, 55 - (obs_year-cohort))); # Extrapolation starts 1 year after the cutoff
##    y_extrapolated = fitted_model(x_extrapolated);
##
##    asfr_cohort_observed = asfr[(asfr["ARDY"] <= obs_year - cohort) & (asfr["Cohort"] == cohort)]; # Filter for ages, and filter for the analysed cohort
##    #print(asfr_cohort_observed)
##    if len(y_extrapolated) == 0:
##        extrapolated_flag = 0
##    else:
##        extrapolated_flag = 1
##        
##    CCF = sum(asfr_cohort_observed["ASFR"]) + sum(y_extrapolated);
##
##    #print(CCF)
##
##    #x_all = np.linspace(12, 55, 44);
##    
##    if plot_flag:
##        sns.lineplot(x = x_extrapolated, y = fitted_model(x_extrapolated), label = str(obs_year))
##    
##
##    return [CCF, extrapolated_flag]
    


def Plot_CCF(start, end, obs_year, asfr):

    x = np.linspace(start, end, end - start + 1)
    #print(x)
    ccf = [Extrapolate_ASFR(int(i), obs_year, asfr[asfr["Cohort"] == int(i)], 1) for i in x] # We filter ASFRs to cohort when passing to the function(?)

    #plt.figure()
    ccf_observed = [v[0] for v in ccf if v[1] == 0]
    ccf_extrapolated = [v[0] for v in ccf if v[1] == 1]
    x_observed = [i for i, v in zip(x, ccf) if v[1] == 0]
    x_extrapolated = [i for i, v in zip(x, ccf) if v[1] == 1]
    if len(ccf_observed) > 0:
        ccf_extrapolated = [ccf_observed[-1]] + ccf_extrapolated
        x_extrapolated = [x_observed[-1]] + x_extrapolated
    c = next(c_it)
    plt.plot(x_observed, ccf_observed, c)
    plt.plot(x_extrapolated, ccf_extrapolated, c+'--') # Add some legend/labels
    #plt.show()

    return 0



def Reconstruct_under12_population(births_total, females, d): # I need to investigate and test this function!!!
    #To do: add a new column - a flag indicating whether the number is observed, extrapolated forwards or extrapolated backwards.
    #Note: this reconstruction doesn't take migration into account
    deaths = d.copy()
    deaths.drop(columns = ["Male", "Total"], inplace=True)
    females = females.merge(deaths, how = 'right', on = ["Age", "Cohort"])
    females.drop(females[females['Age'].astype(float) > 55].index, inplace=True)

    females.loc[females['Age'] == 0, 'Exposure'] = (1/(1+sex_ratio))*females.loc[females['Age'] == 0, 'Year'].map(births_total) # We start at age 0 from births_total corrected for the CONSTANT sex ratio

    for age in range(1, 12): # Forward-propagating reconstruction of under-12s based on death rates
        
        lookup = females.loc[females['Age'] == age - 1].set_index('Cohort')['Exposure']
        mask = (females['Age'] == age)

        females.loc[mask, 'Exposure'] = females.loc[mask, 'Cohort'].map(lookup)

        females.loc[mask, 'Exposure'] = females.loc[mask,'Exposure'] * females.loc[mask]['Cohort'].map(1 - females.loc[females['Age'] == age - 1].set_index('Cohort')['Female'])
        #print(females.loc[mask])                                                               


    females_backprop = females.copy()

    for age in range(11,0,-1): # Back-propagating reconstruction of under-12s based on later 12yo population and death rates
        lookup = females_backprop.loc[females_backprop['Age'] == age + 1].set_index('Cohort')['Exposure']
        mask = (females_backprop['Age'] == age)
        
        females_backprop.loc[mask, 'Exposure'] = females_backprop.loc[mask, 'Cohort'].map(lookup)

        females_backprop.loc[mask, 'Exposure'] = females_backprop.loc[mask,'Exposure'] / females_backprop.loc[mask]['Cohort'].map(1 - females_backprop.loc[females_backprop['Age'] == age + 1].set_index('Cohort')['Female'])

    females.drop(columns = ["Year", "Female"], inplace=True)    
    females_backprop.drop(columns = ["Year", "Female"], inplace=True)
    
    

    females["Exposure"] = np.where(females["Exposure"].isna(), females_backprop["Exposure"], females["Exposure"]) # Replace missing values with backpropagated population

##    with pd.option_context('display.max_rows', None,
##                       'display.max_columns', None,
##                       'display.precision', 3,
##                       ):
##        print(females)
    
    return females
    

def Project_female_population(start, end, asfr, females, d, extrapolate_asfr = False):

    # Beginning from the year [start], project female population for each cohort and year starting from initial data given in [females],
    # based on death rates given in [deaths].
    # To project the numbers of younger females, we also need birth rates, which we either read off from [asfr] or we take only the initial
    # Age Specific Fertility Rates from [asfr] and extrapolate the rest.

    # Problem: the females database only contains numbers of women of age >=12, which we need to correct using the Reconstruct_under12_population function
    
    deaths = d.copy();
    deaths.drop(columns = ["Male", "Total"], inplace=True)
    deaths.rename(columns = {"Female": "Female_DeathRates"}, inplace=True)
     
    females_current = females[females["Cohort"] + females["Age"] == start]; # Female numbers at the start

    females_next = females_current.copy()
    females_all = pd.DataFrame(); # Initialize time series data for female numbers by cohort with empty dataframe
    
    for t in range(start, end+1):
        
        
        births = (1/(1+sex_ratio))*Compute_births(t, females, asfr) # We compute births from Fem distribution and ASFR here.

        if females_next.loc[(females_next['Cohort'] + females_next['Age'] == t) & (females_next['Age'] == 0)].empty: # If there is no row corresponding to the cohort born in year t (current year)
            females_next.loc[max(females_next.index)+1] = [t, 0, births] # This line adds a row. 
        else: # If there is such a row, we need to replace it
            print('replacing a row')
            females_next.loc[(females_next['Cohort'] + females_next['Age'] == t) & (females_next['Age'] == 0), 'Exposure'] = births; # We replace a row instead if it already exists.

        females_all = pd.concat([females_all, females_next], axis = 0, join = 'outer') # Append year t female numbers, including newborns, to females_all
        
        females_next = females_next.merge(deaths, how = 'inner', on = ["Age", "Cohort"])
        females_next["Age"] = females_next["Age"] + 1;
        females_next["Year"] = females_next["Year"] + 1; # Progress age and year by 1. Note: newborns of year 1985 will be 1yo in year 1986.
        females_next["Exposure"] = females_next["Exposure"]*(1-females_next["Female_DeathRates"]); # death rates are applied here
        females_next.drop(columns = ["Year", "Female_DeathRates"], inplace=True)


    females_all = pd.concat([females_all, females_next], axis = 0, join = 'outer') # Append year 'end' female numbers to females_all
    females_all.sort_values(by = ['Cohort', 'Age'], ascending = [True, True], inplace = True)
        
    with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
        print(females_all)
        
    return females_all


def Test_birth_counts(years, asfr, fem, births_total): # Test if birth counts computed from HFD ASFRs and female population
    # matches the birth counts (consistency check). For Poland, the match is within 0.1%, with the former consistently too low

    for y in years:
        births_computed = Compute_births(y, fem, asfr);
        #print(births_total)
        births_observed = births_total[y] # Note that births_total is a Series, not a Dataframe

        print('Year: ', y, ', Births computed: ', "{:.2f}".format(births_computed), ', observed: ', "{:.2f}".format(births_observed))
        print('Error: ', "{:.2f}".format(100*(births_computed - births_observed)/births_observed), '%')

    return 0



def Backtesting(test, asfr, start = 1955, late_cutoff_age = 32, obs_years = []):
    # start corresponds to the earliest cohort included in the analysis
    # Late_cutoff_age corresponds to the cutoff age in the ASFR/CCF extrapolations, for whatever fitting function we use
    # obs_years are the years at which we make the extrapolation. We then test the accuracy of extrapolation by using the full available data.


    
    if test == 'CCF':
        rows = []
        for obs_year in obs_years:
            end = obs_year - late_cutoff_age; # We will forget all data past the late cutoff age
            x = np.linspace(start, end, end - start + 1)
            ccf = [Extrapolate_ASFR(int(i), obs_year, asfr[asfr["Cohort"] == int(i)], 1) for i in x] # We filter ASFRs to cohort when passing to the function(?)
            
            for i, value in zip(x, ccf):
                rows.append((obs_year, i, value[0], value[1]))


        extrapolated_data = pd.DataFrame(rows, columns = ["Observation year", "Cohort", "CCF", "Extrapolated?"])
        print(extrapolated_data)
        #observations = [0]
    
    
    return 0

#b = Compute_births(2005, fem, df)
#print(b)
##cohort = 1965
##sns.lineplot(data = df[df["Cohort"] == cohort], x = "ARDY", y = "ASFR", label = "observed ASFR")
##for obs_year in [1995, 1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019]:
##    Extrapolate_ASFR(cohort, obs_year, df[df["Cohort"] == cohort], 1, 1)
##
##plt.show()

#print(deaths)

fem = Reconstruct_under12_population(births_total, fem, deaths)
#Project_female_population(1975, 1978, df, fem, deaths)

#Test_birth_counts(list(range(1975, 2010)), df, fem, births_total)

plt.figure()
colors = ('k', 'r', 'b', 'g', 'm')
c_it = iter(colors)
Plot_CCF(1955, 1970, 2002, df)
Plot_CCF(1955, 1980, 2012, df)
Plot_CCF(1955, 1990, 2022, df)
plt.show()
#Fit_Gaussian(1975, [28, 36])






