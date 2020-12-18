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

The data in this repository is from one user with IBS between September 2020 and December 2020.

### 2. Data Cleansing

The data is prepared for analysis using the following files:
  * csvCleaner.py (contains methods for parsing information from meal data files)
  * dataFixerUpper.py (combines data from meal files to create clean_data.xlsx as well as the master food list)
  * Analysis1.py (finalizes preparations for analysis and performs analyses)

We experienced many problems with the data at first for several reasons. First, foodDataDownloaded.xlsx contained the dates and times of meals, but did not contain the individual foods eaten in them because it only summarized each meal. foodDataFromPrintout.xlsx did not contain the times, but it did contain each food item. Because both contained the date and title of each meal, these were used to match time to food item (executed on lines 27-68 in dataFixerUpper.py).

Second, the user's myFitnessPal account language is set to Spanish, both meal data files are encoded in Unicode. csvCleaner has methods to interpret the Unicode and convert it to UTF-8 if necessary. No Spanish-English translations had to be made because only meal titles were in Spanish, and these were not necessary for the analysis.

Third, the MyFitnessPal database, though crucial to this project, does not contain ingredient information for foods. Thus, we had to manually record the ingredients for each food (found in food_list_ingredients.xlsx). dataFixerUpper.py creates a list of each food which is saved to food_list.xlsx. From there, the developers have to manually compare this list to food_list_ingredients, and add in any food that is in the former but not in the latter to the latter, as well as copy the ingredients list from the Internet. More detailed information on formatting can be found starting at line 121 in dataFixerUpper.py.

### 3. Analysis

All analysis is performed in the following file:
 * Analysis1.py
 
#### 3.1 Target Format

An observation is one food item.

Non-feature attributes:
   * timestamp
 
Features:
  * each of nutrtional info (fats, etc.)
  * ingredients

Dependent Variables, each at 1 hour increments for X hours: 
  * Values 0-5 (categorical/ordinal)
    - Appetite
    - Stomach Ache
    - Distension
    - Gas
    - Belching
    - Heartburn
 
  * Binary
    - has_symptoms (1 if if Appetite < 3, or any of the rest are > 0)

#### 3.2 Generating Dependent Variable Data

For each observation, a dict is produced. The keys are strings of the format '{startTime}-{endTime}' that denote the time interval over which getSymptomsInInterval() returns the maximum values (i.e. severity) of each symptom variable, as well as whether or not a symptom was experienced (has_symptoms). The values are data frames that contain one entry per observation, and each entry contains the values produced by getSymptomsInInterval(). So, for example, if a food item was eaten at 6:00PM on 10/08/20, hours is set to 2, and step is set to 3, then there would be two keys: '0-3' and '1-4'. getSymptomsInInterval() would produce the maximum values of each symptom between 6:00PM and 9:00PM on 10/08/20 and place that information in one row of the data frame corresponding to '0-3'. It would do the same thing for the times between 7:00PM and 10:00PM on 10/08/20 but for the '1-4' key.

Because we want to ignore times when the user is asleep, we currently have the program set to ignore the times between 2 hours after the final meal of a day and 1 hour before the first meal of the next day. This, while not perfectly capturing when the user is actually asleep every time, very closely conforms to their sleeping habits. This aspect of the project will be discussed further in the Results and Discussion section.


#### 3.3 Analyses

We use three different classification methods:
 * K-Nearest Neighbors (n_neighbors = 5)
 * Logistic Regression
 * Decision Tree
 
For each, we split the data into training and test sets (test size = 0.4), and balance the data so that there is a roughly equal amount of 1's (has_symptoms == True) and 0's. We scale the features using the min-max scaler. The tests are run for every time interval; thus, if hours is set to 12, we run each of the three tests 12 times.

### 4. Results and Discussion

As of 12/17/20, the analyses run successfully. With that said, they do not have as great accuracy as we had hoped. Accuracy tends to be around .5, with few time blocks achieving upwards of .65 and many below .5. But, because 1's and 0's don't tend to be evenly distributed, the F1 score may be a better measure of accuracy. The F1 scores tend to be higher than accuracy, usually above .6. While not great, this gives us hope that adjusting parameters, improving data collection, and improving generateDVs() so that it ignores all times when the user is asleep will result in a significant increase to F1 scores.

Data collection for anyone can be a challenge because it requires consistency, and it can simply be quite annoying to do. This process could be streamlined by an app or other UI to make it easier for users to record their data.

We also plan to update generateDVs() to ignore all hours when the user is asleep. Given that this user did not log when they were asleep, we are limited as to how we choose to ignore certain hours. Currently, we assume the user sleeps between two hours after their final meal and one hour before their first meal the next day. The program only ignores this for the final meal of the day, so it needs to be updated to ignore those hours for every meal of the day. For future users, we plan to have them log when they are alseep, as this will be the most effective and feasible way to ignore sleep hours.

We also plan to incorporate visualization tools so that users can make sense of the data without the need for an expert to interpret it for them.

### Further Research

Given that this is the first of its kind, more research is certainly required for it to reach its full potential. We tested it on one subject with IBS, and we only tracked certain relevant symptoms. We can certainly generalize the program to other diseases, symptoms, etc, and perhaps it can include other independent variables such as stress level and exercise. Of course, more can be accomplished with more volunteers thus more data.
