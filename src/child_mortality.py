import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prettytable import PrettyTable
import random
import scipy
import scipy.stats as stats
import scipy.interpolate as interpolate
import pylab
from matplotlib.ticker import FormatStrFormatter

DEATH_AGE = 0

CSV_KEYS_PRENATAL = {
    'percentageKey': 'Percentual de gestantes com sete ou mais consultas de pré-natal / ano',
    'year': 'Ano',
    'cityId': 'Código município IBGE',
}

CSV_KEYS_DEATHS = {
    'numberOfDeaths': 'Óbitos',
    'cityId': 'res_codmun_adotado: Descending',
    'deathAge': 'idade_obito: Descending',
    'year': 'ano_obito: Descending',
}

CSV_KEYS_BIRTHS = {
    'numberOfBirths': 'Total',
    'cityId': 'res_codmun_adotado: Descending',
    'year': 'ano_nasc: Descending',
}

CSV_PATHS = {
    'birth': '../fiocruz/birth_grouped_by_year_city/data.csv',
    'deaths': '../fiocruz/deaths_between_0_5_years_grouped_by_age_city_year/data.csv',
    'prenatal': '../dados.gov/prenatal/prenatal_city_year.csv'
}

# Raw data
birthData = pd.read_csv(CSV_PATHS['birth'])
deathsData = pd.read_csv(CSV_PATHS['deaths'])
prenatalData = pd.read_csv(CSV_PATHS['prenatal'])

# filtering by percentage > 0
prenatalData = prenatalData.loc[(
    prenatalData[CSV_KEYS_PRENATAL['percentageKey']] > 0.00)]

# converting data to numeric
birthData[CSV_KEYS_BIRTHS['numberOfBirths']] = pd.to_numeric(birthData[CSV_KEYS_BIRTHS['numberOfBirths']].str.replace(',', ''))
birthData[CSV_KEYS_BIRTHS['year']] = pd.to_numeric(birthData[CSV_KEYS_BIRTHS['year']].str.replace(',', ''))
deathsData[CSV_KEYS_DEATHS['year']] = pd.to_numeric(deathsData[CSV_KEYS_DEATHS['year']].str.replace(',', ''))
deathsData[CSV_KEYS_DEATHS['numberOfDeaths']] = pd.to_numeric(deathsData[CSV_KEYS_DEATHS['numberOfDeaths']].str.replace(',', ''))

deathsData = deathsData.loc[(deathsData[CSV_KEYS_DEATHS['deathAge']] <= DEATH_AGE)]

# Retrieve the IBGE ids to use
# 50 greatest brazilian cities 
cityIdsToUse = [355030,330455,530010,292740,230440,310620,130260,410690,261160,431490,520870,150140,351880,350950,211130,330490,270430,330170,240810,500270,221100,354870,250750,330350,354780,354990,353440,260790,354340,317020,355220,311860,280030,291080,510340,420910,313670,411370,520140,110020,150080,320500,330330,330045,330100,320520,420540,430510,160030,352940]
#cityIdsToUse = prenatalData[CSV_KEYS_PRENATAL['cityId']].unique()

def getMortalityRate(birthData, prenatalData, deathsData, cityIdsToUse, year):
    mergedData = []
    for cityId in cityIdsToUse:
        # filtering birthData by year and cityId
        birthsSet = birthData.loc[
            (birthData[CSV_KEYS_BIRTHS['cityId']] == cityId) &
            (birthData[CSV_KEYS_BIRTHS['year']] == year)]

        # filtering deathsData by year and cityId
        deathsSet = deathsData.loc[
            (deathsData[CSV_KEYS_DEATHS['cityId']] == cityId) &
            (deathsData[CSV_KEYS_DEATHS['year']] == year)]

        # filtering prenatalData by year and cityId
        prenatalSet = prenatalData.loc[
            (prenatalData[CSV_KEYS_PRENATAL['cityId']] == cityId) & 
            (prenatalData[CSV_KEYS_PRENATAL['year']] == year)]

        if (birthsSet.empty or deathsSet.empty or prenatalSet.empty):
            print('no good data.. birth:', birthsSet.empty, 'deaths: ', deathsSet.empty, 'prenatal: ', prenatalSet.empty)
            continue

        try:
            numberOfDeaths = int(deathsSet['Óbitos'].sum())
            numberOfBirths = int(birthsSet['Total'].sum())
        except:
            continue

        if (numberOfBirths == 0):
            print('no good data... number of births is zero')
            continue

        mergedData.append({
            'year': year,
            'numberOfBirths': numberOfBirths,
            'numberOfDeaths': numberOfDeaths,
            'cityId': cityId,
            'mortalityRate': (numberOfDeaths / numberOfBirths) * 1000,
            'cityName': deathsSet['Município de residência'].unique()[0],
            'percentagePrenatal': prenatalSet[CSV_KEYS_PRENATAL['percentageKey']].unique()[0]
        })
    
    return mergedData

def scatterplot(x_data, y_data, x_label, y_label, title):

    # Create the plot object
    _, ax = plt.subplots()

    # Plot the data, set the size (s), color and transparency (alpha)
    # of the points
    ax.scatter(x_data, y_data, s=30, color='#539caf', alpha=0.75, label='City')
    ax.scatter(np.mean(x_data), np.mean(y_data), s=30, color='#ff0000', alpha=0.75, label='Mean')
    
    # regression
    polyfit =np.poly1d(np.polyfit(x_data, y_data, 1))
    y_polyval = np.polyval(polyfit, x_data)
    correlation = np.corrcoef(x_data, y_data)
    
    plt.plot(x_data, y_polyval, color='#af5f53', label='Regression')

    points = []
    for cityName, x, y, y_fit in zip(cityNames, x_data, y_data, y_polyval): 
        points.append((x,y))
        if (y_fit >= 15 or y_fit <= 10) and False:
            plt.annotate(
                cityName,
                xy=(x, y), xytext=(-15, -15),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

        if y < 8 and False:
            plt.annotate(
                cityName,
                xy=(x, y), xytext=(20, 20),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0),
                arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

    # Label the axes and provide a title
    ax.set_title(title + '\n {} cidades analisadas'.format(len(x_data)))
    ax.set_xlabel(x_label + '\nCorrelation: {}'.format(correlation))
    ax.set_ylabel(y_label)

    plt.legend()
        
    plt.show()

def yearByYearPlot(years, mortality_rate_means, prenatal_means, title):
    _, ax = plt.subplots()
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.xaxis.set_ticks(np.arange(years[0] - 1, years[len(years) - 1] + 1))
    plt.xticks(rotation=75)

    if mortality_rate_means:
        ax.set_title(title)
        ax.set_ylabel('Taxa mortalidade infantil', color='b')
        ax.set_xlabel('Ano')
        ax.plot(years, mortality_rate_means, color='b', marker='o', label='Regression')

    if prenatal_means:        
        ax2 = ax.twinx() if mortality_rate_means else ax
        ax2.set_ylabel('% de grávidas com ao menos 7 pré natal', color='g')
        ax2.plot(years, prenatal_means, color='g', marker='x', label='Regression')        
        
    _.tight_layout()
    plt.show()

#years = [2010, 2011, 2012, 2013, 2014]
years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]
mortalityMean = []
prenatalMean = []

for year in years:
    data = getMortalityRate(birthData, prenatalData, deathsData, cityIdsToUse, year)
    mortalityRate = []
    percentagePrenatal = []
    cityNames = []
    
    t = PrettyTable(['City', 'PercentagePrenatal', 'MortalityRate'])
    for d in data:
        mortalityRate.append(d['mortalityRate'])
        percentagePrenatal.append(d['percentagePrenatal'])
        cityNames.append(d['cityName'])
        t.add_row([d['cityName'], d['percentagePrenatal'], '{0:.2f}'.format(d['mortalityRate'])])
    
    print(t)

    #mortalityMean.append(sum(mortalityRate) / len(mortalityRate))  
    #prenatalMean.append(sum(percentagePrenatal) / len(percentagePrenatal))
    mortalityMean.append(np.median(mortalityRate))
    prenatalMean.append(np.median(percentagePrenatal))
    
    scatterplot(x_data=percentagePrenatal,
                y_data=mortalityRate,
                x_label='Porcentagem de grávidas que fizeram ao menos 7 pré natal',
                y_label='Taxa mortalidade infantil',
                title='Taxa de Mortalidade infantil x Acesso ao prenatal ({})'.format(year))

yearByYearPlot(years, mortalityMean, prenatalMean, 'Mortalidade infantil e acesso ao pré natal durante os anos')
#yearByYearPlot(years, [], prenatalMean, 'Acesso ao pré natal durante os anos')
#yearByYearPlot(years, mortalityMean, [], 'Mortalidade infantil durante os anos')