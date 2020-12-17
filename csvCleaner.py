# Author: Pierce Klein

import pandas as pd
from IPython.display import display, HTML
import string
from dateutil.parser import *
from datetime import *
DEFAULT = datetime(2003, 9, 25)

# Checks the current row of data downloaded from MyFitnessPal and determines if it's a date, meal name,
# the word "FOODS," or a food item. Returns the type and/or the string value
def categorize_entry(entry):
    # categories are food item, meal name, FOODS and date

    # check if entry is FOODS
    if(entry == 'FOODS' or 'TOTAL' in entry):
        return ['FOODS', 0]
    
    # check if entry is a meal
    if('Breakfast' in entry):
        return ['meal name', 'Breakfast']
    elif('Bocado' in entry):
        if('1' in entry):
            return ['meal name', u'Bocado 1']
        else:
            return ['meal name', u'Bocado 2']
    elif('Almuerzo' in entry):
        return ['meal name', u'Almuerzo']
    elif('Cena' in entry):
        if('1' in entry):
            return ['meal name', u'Cena 1']
        else:
            return ['meal name', u'Cena 2']

    # check if entry is a date
    try:
        parse(entry)
    except:
        return ['food name', entry]
    else:
        return ['date', parse(entry)]

# gets the time of the meal from the downloaded CSV and returns it
def match_meal_to_time(downloaded_df, date, meal):

    for i in range(len(downloaded_df.index)-1):

        download_date = downloaded_df.iloc[i]['Date']
        download_meal = downloaded_df.iloc[i]['Meal']
        meal_time = downloaded_df.iloc[i]['Time']

        if(date == download_date and meal.split() == download_meal.split()):
            return meal_time

# makes a nasty Unicode string into a nice UTF-8 string
def clean_up_unicode(unicode_string):
    
    clean_string = unicode_string.encode('utf-8')
    clean_string = clean_string.replace('\xa0', ' ')
    clean_string = clean_string.replace('\xc2', ' ')
    clean_string = clean_string.replace('  ', ' ').replace('.','')
    clean_string = clean_string.strip()
    clean_string = clean_string.lower()

    return clean_string

# removes g & mg from Carbs(g), Fat(g), Protein(g), Sodium(mg), Sugars(g), Fiber(g)
# also sets '--' to 0
def remove_units(string):
    
    string = string.encode('utf-8')
    
    if('-' in string):
        string = 0
    else:
        string = int(string.replace('m', '').replace('g','').replace(',',''))
        
    return string