#!/usr/bin/env python
# coding: utf-8

# Author: Pierce Klein

# In[3]:


import pandas as pd
from IPython.display import display, HTML
import csvCleaner # module I created to assist in cleaning up the data
from datetime import *

# load the meal summary report downloaded from MyFitnessPal (requires Premium membership to download)
meal_summary_df = pd.read_excel('C://Users/Pierce/Documents/foodDiary/foodDataDownloaded.xlsx')

# Copied from "View Full Report (printable)" link below daily entry on MyFitnessPal. It's an HTML table I copied
# and pasted into an Excel spreadhsheet
food_from_printout_df = pd.read_excel('C://Users/Pierce/Documents/foodDiary/foodDataFromPrintout.xlsx')


# In[4]:


# Load data into a Pandas Dataframe

column_names = ['Date', 'Time', 'Meal', 'Food', 'Calories', 'Carbs', 'Fat',
                'Protein', 'Cholest', 'Sodium', 'Sugars', 'Fiber']

# push each entry into a list and then use that list as the data for the dataframe
temp_list = []

# initial date is the day the user began tracking their meals on MyFitnessPal
current_date = datetime(2020, 9, 21, 0, 0)
current_meal = 'Breakfast'

# first entry is the column name
temp = food_from_printout_df.columns[0]
current_entry = csvCleaner.categorize_entry(temp)

# every other entry is a data entry
for i in range(len(food_from_printout_df.index)):
    
    # Categorize each entry
    temp = food_from_printout_df.iloc[i][0]
    current_entry = csvCleaner.categorize_entry(temp)
    
    if(current_entry[0] == 'FOODS'):
        pass
    
    elif(current_entry[0] == 'date'):
        current_date = current_entry[1]
        
    elif(current_entry[0] == 'meal name'):
        current_meal = current_entry[1]
        
    else:
        data_to_append = [current_date]
        current_time = csvCleaner.match_meal_to_time(meal_summary_df, current_date, current_meal)
        data_to_append.append(current_time)
        data_to_append.append(current_meal)
        
        for col in food_from_printout_df.columns:
            data_to_append.append(food_from_printout_df.iloc[i][col])
            
        temp_list.append(data_to_append)

clean_data_df = pd.DataFrame(data=temp_list, columns=column_names)

# Move units from within cells to column names so that cell data can be int, and because this is far more readable
columns_to_change = ['Carbs', 'Protein','Fat', 'Cholest', 'Sodium', 'Sugars', 'Fiber']
for col in columns_to_change:
    clean_data_df[col] = clean_data_df[col].map(lambda(x): csvCleaner.remove_units(x))
    
clean_data_df = clean_data_df.rename(columns={'Carbs': 'Carbs (g)', 'Fat': 'Fat (g)', 'Protein': 'Protein (g)',
                                              'Cholest': 'Cholest (mg)', 'Sodium': 'Sodium (mg)', 'Sugars': 'Sugars (g)',
                                              'Fiber': 'Fiber (g)'})

display(HTML(clean_data_df.tail().to_html()))


# In[3]:


with pd.ExcelWriter('clean_data.xlsx') as writer:
    clean_data_df.to_excel(writer, sheet_name='Meals')


# In[4]:


# Get list of each unique food

food_list_df = clean_data_df.drop_duplicates(subset='Food')

# We only want the names of the foods for this list
food_list_df = pd.DataFrame(data=food_list_df['Food'])

# Names from MyFitnessPal contain amount of servings, separated from the food name by a comma. For example,
# one entry might be "clementine, 2 servings." Sometimes there is a comma within the name of the food, but cutting off
# everything after the first comma at least produces the same truncated name every time. This way we can match a food name
# from this list to a food in the clean_data_df regardless of serving size and it will work every time
for i in range(len(food_list_df.index)):
    x = food_list_df.iloc[i]['Food'].find(',')
    food_list_df.iloc[i]['Food'] = food_list_df.iloc[i]['Food'][0:x]

#sort alphabetically and drop dupilcates
food_list_df = food_list_df.sort_values('Food')
food_list_df = food_list_df.drop_duplicates(subset='Food')

display(HTML(food_list_df.head().to_html()))


# In[5]:


with pd.ExcelWriter('food_list.xlsx') as writer:
    food_list_df.to_excel(writer, sheet_name='Foods')


# ### The above code created all the "raw" data. Now you have to manually double check that food_list and food_list_ingredients have the all the same foods.
# 
# ##### Every time the user eats a new food, you must manually add that food into the food_list_ingredients spreadsheet, along with its ingredients.
# ##### Make sure to delete parantheticals (i.e. GUM (XANTHAN GUM, SODIUM ALGINATE, GUAR GUM) is listed as an ingredient for Udi's Gluten-Free Hamburger Buns. Change it to "xanthan gum, sodium alginate, guar gum" to properly read in these ingredients)
# 
# ### This nextm part will handle getting all the ingredients into their own columns and populating the rows with binary data to tell you whether that ingredient is present in each food.

# In[8]:


# First, a master list of every ingredient.
ingredient_list = ['salt'] # I know salt is in a lot of stuff, just didn't want to start with an empty list
food_list_ingredients_raw = pd.read_excel('C://Users/Pierce/Documents/foodDiary/food_list_ingredients.xlsx')

temp_food_list = []

for i in range(len(food_list_ingredients_raw.index)):
    
    # clean up the nasty mess that is Unicode (The user's MyFitnessPal language is set to Spanish)
    temp_food_list.append(csvCleaner.clean_up_unicode(food_list_ingredients_raw.iloc[i]['Ingredients']))

for i in range(len(food_list_ingredients_raw.index)):
    # make a list of current food's ingredients
    clean_string = csvCleaner.clean_up_unicode(food_list_ingredients_raw.iloc[i]['Ingredients'])
    current_ingredients = clean_string.split(', ')
    
    # add in new ingredients to the ingredient list
    for ingredient in current_ingredients:
        if(ingredient not in ingredient_list):
            ingredient_list.append(ingredient)

ingredient_list = sorted(ingredient_list)
#print('done') # leftover from this being in a Jupyter Notebook


# In[9]:


# Now to make the master food list
master_food_list = []

# convert lists of ingredients into binary inputs for each ingredient to put into final data frame
for i in range(len(food_list_ingredients_raw.index)):
    
    current_entry = [food_list_ingredients_raw.iloc[i]['id'], food_list_ingredients_raw.iloc[i]['Food']]
    
    # make a list of current food's ingredients, all lower case
    clean_string = csvCleaner.clean_up_unicode(food_list_ingredients_raw.iloc[i]['Ingredients'])
    current_ingredients = clean_string.split(', ')
    
    # strip leading and tailing whitespace, convert to UTF-8, and set all capitals to lower case
    for i in range(0,len(current_ingredients)):
        current_ingredients[i] = current_ingredients[i].strip().encode('utf-8')
        current_ingredients[i] = current_ingredients[i].lower()
    
    # 1 for every ingredient the food contains, 0 otherwise
    for ingredient in ingredient_list:
        if(ingredient in current_ingredients):
            current_entry.append(1)
        else:
            current_entry.append(0)
    
    master_food_list.append(current_entry)

#print('done') # leftover from this being in a Jupyter Notebook


# In[10]:


column_names = ['id', 'food'] + ingredient_list
master_food_list_df = pd.DataFrame(data=master_food_list, columns=column_names)

display(HTML(master_food_list_df.tail().to_html()))


# In[11]:


with pd.ExcelWriter('master_food_list.xlsx') as writer:
    master_food_list_df.to_excel(writer, sheet_name='Foods')


# In[46]:




