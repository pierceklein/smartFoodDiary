# Smart Food Diary

## Purpose

The Smart Food Diary is intended for people with chronic diet-related issues such as irritable bowel syndrome (IBS). It can be extremely difficult to narrow down exactly which foods cause discomfort because different people's symptoms can be caused by completely different triggers. It often comes down to the fine print on the ingredients list; it can be something as seemingly inconsequential as guar gum or soy lecithin, etc.

Via users' reports of their meals and symptoms, this application looks for associations between specific ingredients and severity of symptoms in predetermined time blocks after consuming those meals.

## Methodology

### 1. Data Collection

Raw data can be found in the following three files:
  * foodDataDowloaded.xlsx (meals)
  * foodDataFromPrintout.xlsx (meals)
  * symptoms.xlsx (symptoms)

Users record their meals using MyFitnessPal. This application uses a user-generated database of nutrition information for most foods with the exception of ingredients, making it highly useful for the Smart Food Diary. Users who purchase a Premium subscription may also download a CSV report that contains summaries of all of their meals, including the time at which they were eaten (see foodDataDownloaded.xlsx). User is required to download the CSV report as well as one other file: the printable report found on myfitnesspal.com at the bottom of the daily meal entry page (see foodDataFromPrintout.xlsx).

Users report symptoms on a 0-5 scale on symptoms.xlsx. For each symptom EXCEPT Appetite, 0 means no discomfort, 5 means extremely severe. For appetite, 0 means that the user cannot stomach food, 3 is normal appetite, and 5 is starving.

### 2. Data Cleansing

The data is prepared for analysis using the following files:
  * csvCleaner.py (contains methods for parsing information from meal data files)
  * dataFixerUpper.py (combines data from meal files to create clean_data.xlsx as well as the master food list)
  * 

We experienced many problems with the data at first
