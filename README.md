# TFR-Project
Projections of fertility rates, birth rates and population size

The main goal of the project is to extrapolate fertility rates and birth rates, rather than population itself. So the focus is not on death rates (except death rates of young women, as they do impact birth numbers to a small degree), but rather on fertility rates.

1. Currently, the input data is saved in .csv manually (automatic data download functionality coming soon). The .csv data is then read by the python program and cleaned.
2. The function Reconstruct_under12_population calculates the female population by age for ages below 12, as this data is missing from the input. The numbers are either calculated forwards starting from birth rates and multiplying by death rates, or backwards - starting from the population of females of age 12 and successively dividing by death rates. Note that this neglects migration, which (for Poland) leads to errors of the order of 1%.
3. Functions Plot_by_year and Plot_by_cohort provide basic plotting functionality, plotting the ASFR (Age Specific Fertility Rate). The function Plot_CCF plots the completed cohort fertility, either observed or extrapolated some years into the future. (CCF stands for Completed Cohort Fertility)
4. The function Fit_Gaussian fits the function c*exp(-a*(x-x0)^2) (where x is the woman's age) to ASFR between specified ages A and B. This is a relatively good model of ASFR decay for older women (35+).
5. The function Extrapolate_ASFR extrapolates ASFRs for a given cohort, until that cohort turns 55.
6. There are functions for computing births numbers from given data (observed or extrapolated) as well as for extrapolating birth numbers (which is done in 2 steps: first, extrapolate ASFRs, then compute births). However, this is incomplete as there is as yet no functionality to extrapolate ASFRs for women younger than 32.
7. Project_female_population uses the Compute_births function (this should be updated soon to use extrapolated births instead) to project female population, by age, into the future.
8. The function Backtesting provides some basic backtesting functionality, comparing ASFRs and CCFs extrapolated at some point in the past to subsequently observed ones. 
