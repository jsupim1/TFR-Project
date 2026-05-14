import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from astropy import modeling
from scipy.optimize import least_squares
import Model_ASFR

sex_ratio = 1.055


#na_values = ["."]

df = pd.read_csv("Poland_ASFR.csv", dtype = {"ARDY": float}, na_values = {'ARDY': ["12-", "55+"]});
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

deaths["Cohort"] = deaths["Year"] - deaths["Age"];

births_total = births.groupby('Year')["Total"].sum();

def Plot_by_year(Years):

    for year in Years:
        sns.lineplot(data = df[df["Year"] == year], x = "ARDY", y = "ASFR", label = "Year: " + str(year))

    return 0

def Plot_by_cohort(Cohorts, ax = None):

    if not ax:
        fig, ax = plt.subplots()

    else:
        fig = ax.figure

    for cohort in Cohorts:
        sns.lineplot(data = df[df["Cohort"] == cohort], x = "ARDY", y = "ASFR", label = "Cohort: " + str(cohort), ax = ax)

    return fig, ax

#Plot_by_cohort([1950, 1960, 1970, 1980, 1990, 2000])
#plt.show()

def fun(V, x, y):

    return (V[0]*np.array(Model_ASFR.ASFR_function(V[1:], x)) - y)


def Fit_ASFR(cohort, cutoff_ages, plot = 0): # Fit full ASFR schedule (including scaling constant) to observed cohort ASFRs
    
    df_cohort = df[df["Cohort"] == cohort] #Filter for cohort

    df_train = df_cohort[(df_cohort["ARDY"] >= cutoff_ages[0]) & (df_cohort["ARDY"] <= cutoff_ages[1])] # We only fit to ASFRs between the cutoff ages
    
    x_train = df_train["ARDY"]
    y_train = df_train["ASFR"]

    x_all = np.linspace(12, 55, 44);

    


    res = least_squares(fun, np.array([1,0.5, 2, 5, 5, 18, 30]), \
          bounds = ([0.5, 0, 1.95, 0.1, 0.1, 15, 18], [2, 1, 2.05, 6, 10, 35, 40]), \
                        args = (x_train, y_train), verbose = 0)

    if plot:
        y_all = res.x[0]*np.array(Model_ASFR.ASFR_function(res.x[1:], x_all))
        fig, ax = plt.subplots()
        ax.plot(x_all, y_all)
        return [res, ax]

    #extrapolated_values = res.x_all
    
    return res

def Fit_Gaussian(cohort, cutoff_ages): # Fit a Gaussian function to ASFRs - this fitted Gaussian can be extrapolated beyond the late cutoff age
    
    df_cohort = df[df["Cohort"] == cohort] #Filter for cohort

    df_train = df_cohort[(df_cohort["ARDY"] >= cutoff_ages[0]) & (df_cohort["ARDY"] <= cutoff_ages[1])] # We only fit to ASFRs between the cutoff ages
    
    x_train = df_train["ARDY"]
    y_train = df_train["ASFR"]
 
    x_all = np.linspace(12, 55, 44);


    fitter = modeling.fitting.LevMarLSQFitter()
    model = modeling.models.Gaussian1D(amplitude = 0.2, mean = 25, stddev = 5)   # Initial values for the fitting algorithm to be revised
    fitted_model = fitter(model, x_train, y_train)

    #sns.lineplot(data = df_cohort, x = "ARDY", y = "ASFR")
    #sns.lineplot(x = x_all, y = fitted_model(x_all))
    #plt.show()

    return fitted_model # Returns a function



def Extrapolate_ASFR(cohort, obs_year, asfr, method = 'Gaussian', ccf_only = 0, plot_flag = 0, ax = []):

    if method == 'Gaussian':
        if obs_year - cohort <= 32: # If highest observed age is <33, extrapolation is too unreliable or it's impossible
            return pd.DataFrame()   
        
        fitted_model = Fit_Gaussian(cohort, [28, obs_year-cohort])
        x_extrapolated = np.linspace(min(obs_year-cohort+1, 55), 55, max(0, 55 - (obs_year-cohort))); # Extrapolation starts 1 year after the cutoff
        y_extrapolated = fitted_model(x_extrapolated);


    elif method == 'full':
        if obs_year - cohort <= 29: # If highest observed age is <30, extrapolation is too unreliable or it's impossible
            return pd.DataFrame()

        res = Fit_ASFR(cohort, [15, obs_year-cohort], 0)
        x_extrapolated = np.linspace(min(obs_year-cohort+1, 55), 55, max(0, 55 - (obs_year-cohort))); # Extrapolation starts 1 year after the cutoff
    
        y_extrapolated = res.x[0]*np.array(Model_ASFR.ASFR_function(res.x[1:], x_extrapolated ))


    
    # From the particular cohort, only include ages observed up to the obs_year
    asfr_cohort_observed = asfr[(asfr["ARDY"] <= obs_year - cohort) & (asfr["Cohort"] == cohort)];        

    if len(y_extrapolated) == 0:
        extrapolated_flag = 0
    else:
        extrapolated_flag = 1

    if ccf_only:
        CCF = sum(asfr_cohort_observed["ASFR"]) + sum(y_extrapolated);

        #print(CCF)
    
        if plot_flag:
            if not ax:
                fig, ax = plt.subplots()
            else:
                fig = ax.figure
                    
            sns.lineplot(x = x_extrapolated, y = y_extrapolated, label = "ASFR extrapolated in: " + str(obs_year))
    

        return [CCF, extrapolated_flag]

    else:
        asfr_extrapolated = pd.DataFrame([ [i, j, 1] for i, j in zip(x_extrapolated, y_extrapolated)], columns = ["ARDY", "ASFR", "Extrapolated?"])

        asfr_extrapolated['Year'] = cohort + asfr_extrapolated['ARDY']
        asfr_extrapolated['Cohort'] = float(cohort)

        if plot_flag:
            if not ax:
                fig, ax = plt.subplots()
            else:
                fig = ax.figure
            sns.lineplot(x = x_extrapolated, y = y_extrapolated, label = "ASFR extrapolated in: " + str(obs_year))
    
        #print(asfr_extrapolated)
        
        return asfr_extrapolated


    return 0
    
def Extrapolate_births(start, end, fem, asfr_observed): # Focus on this and improve it

    asfr_extrapolated = pd.DataFrame()
                    
    for i in range(0, 8): # Modify the range
        a = Extrapolate_ASFR(1975+i, start, asfr_observed)
        asfr_extrapolated = pd.concat([asfr, a]) # So far, this dataframe contains ASFRs for ages >~ 32


    

    return [Compute_births(y, fem, asfr_extrapolated) for y in range(start, end)]


def Compute_births(years, fem, asfr): # We could modify this to take a series of years as argument

    if type(years) != list:
        return Compute_births([years], fem, asfr)[0]
        
    fem_years = fem[(fem["Cohort"] + fem["Age"]).isin(years)] # Filter women numbers for given years
    #print(fem_year)

    asfr = asfr[asfr["Year"].isin(years)] # Filter ASFRs for given years
    #print(asfr)

    fem_years = fem_years.merge(asfr.set_index("Cohort"), left_on = ("Cohort", "Age"), right_on = ("Cohort", "ARDY"), how = 'inner') # Join the two dataframes
    fem_years["Live_births"] = fem_years["Exposure"]*fem_years["ASFR"]
    print(fem_years)

    births = []
    for i, year in enumerate(years):
        births.append(sum(fem_years[((fem_years["Cohort"] + fem_years["Age"]) == year)]["Live_births"])) # Births in a given year are the sum of F_i*asfr_i, where i is the female age

    return births



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

    #for y in years:
    births_computed = Compute_births(years, fem, asfr);
        #print(births_total)
    births_observed = [births_total[y] for y in years] # Note that births_total is a Series, not a Dataframe
    for i, y in enumerate(years):
        print('Year: ', y, ', Births computed: ', "{:.2f}".format(births_computed[i]), ', observed: ', "{:.2f}".format(births_observed[i]))
        print('Error: ', "{:.2f}".format(100*(births_computed[i] - births_observed[i])/births_observed[i]), '%')

    return 0



def Backtesting(test, asfr, start = 1955, late_cutoff_age = 32, obs_years = [], return_mode = 'errors'):
    # start corresponds to the earliest cohort included in the analysis
    # Late_cutoff_age corresponds to the cutoff age in the ASFR/CCF extrapolations, for whatever fitting function we use
    # obs_years are the years at which we make the extrapolation. We then test the accuracy of extrapolation by using the full available data.

    abs_error = []
    mean_error = []
    
    if test == 'CCF':
        rows = []
        for obs_year in obs_years:
            end = obs_year - late_cutoff_age;  # We will extrapolate CCFs for cohorts who are now older than late_cutoff_age
            x = np.linspace(start, end, end - start + 1)
            ccf = [Extrapolate_ASFR(int(i), obs_year, asfr[asfr["Cohort"] == int(i)], 1) for i in x] # We filter ASFRs to cohort when passing to the function(?)
            
            for i, value in zip(x, ccf):
                rows.append((obs_year, i, value[0], value[1]))


        extrapolated_data = pd.DataFrame(rows, columns = ["Observation year", "Cohort", "CCF", "Extrapolated?"])
        #print(extrapolated_data)
        #print(asfr)
        ccf_observed = asfr[(asfr['Cohort'] <= asfr['Year'].max() - 55) & (asfr['Cohort'] > asfr['Year'].min() - 15)].groupby('Cohort')['ASFR'].sum()
        ccf_observed = ccf_observed.to_frame(name = 'CCF')
        ccf_observed.reset_index(inplace = True)
        #print(ccf_observed)
        
        plt.figure(num = 27)
        sns.lineplot(data = ccf_observed, x = 'Cohort', y = 'CCF', label = 'Observed CCF')
        for obs_year in obs_years:
            sns.lineplot(data = extrapolated_data[extrapolated_data["Observation year"] == obs_year], x = 'Cohort', y = 'CCF', label = 'Extrapolated CCF in year ' + str(obs_year))

        #plt.show()
        
            merged_data = pd.merge(left = extrapolated_data[extrapolated_data["Observation year"] == obs_year], right = ccf_observed, how = 'inner', on = ['Cohort'], suffixes = ['_extrapolated', '_observed'])

            print(merged_data)
            diff = merged_data['CCF_extrapolated'] - merged_data['CCF_observed']
            #print(diff)
            abs_error.append(sum(abs(diff))/len(diff))
            mean_error.append(sum(diff)/len(diff))
            
        
        return [[a, b] for a, b in zip(abs_error, mean_error)]

    elif test == 'ASFR':
        extrapolated_data = pd.DataFrame()

        for obs_year in obs_years:
            end = obs_year - late_cutoff_age; # We will extrapolate ASFRs for cohorts who are now older than late_cutoff_age
            x = np.linspace(start, end, end - start + 1)
            for i in x:
                ex_asfr = Extrapolate_ASFR(int(i), obs_year, asfr, 0)

                extrapolated_data = pd.concat([extrapolated_data, ex_asfr])

##            with pd.option_context('display.max_rows', None,
##                       'display.max_columns', None,
##                       'display.precision', 3,
##                       ):
##                print(extrapolated_data)

            #print(asfr[asfr['Year'] >= obs_year])

            merged_data = pd.merge(left = extrapolated_data, right = asfr[asfr['Year'] >= obs_year], how = 'inner', on = ['Cohort', 'Year', 'ARDY'], suffixes = ['_extrapolated', '_observed'])

            print(merged_data)
            diff = merged_data['ASFR_extrapolated'] - merged_data['ASFR_observed']
            #print(diff)
            abs_error.append(sum(abs(diff))/len(diff))
            mean_error.append(sum(diff)/len(diff))

            
            
        #return merged_data
        if return_mode == 'errors':
            return [[a, b] for a, b in zip(abs_error, mean_error)]
        else:
            return merged_data
    
    
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

#plt.figure()
colors = ('k', 'r', 'b', 'g', 'm')
c_it = iter(colors)
##Plot_CCF(1955, 1970, 2002, df)
##Plot_CCF(1955, 1980, 2012, df)
##Plot_CCF(1955, 1990, 2022, df)
##plt.show()
#Fit_Gaussian(1975, [28, 36])






