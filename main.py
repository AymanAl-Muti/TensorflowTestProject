# Name: Ayman Almuti
# Date: January 8'th
# Program name: Machine learning incorparated into some character maker
# Purpose: Player makes a character from some stats and then the machine guesses how liely they are to survive a boss fight.

# Imports some libraries for the code
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.indexes import numeric
import tensorflow as tf
from tensorflow import feature_column
import numpy as np
import inquirer
from IPython.display import clear_output
from tensorflow.python.feature_column.feature_column_v2 import NumericColumn
import random
import csv
import os
from sqlFunctions import *

# prepares the system for the CUDA and then clears the output.
os.system('cls' if os.name == 'nt' else 'clear')
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

print("\nCan you please give us a username: ")
CCUsername = input()

#prepares the training data that I created
trainingSetDF = pd.read_csv("https://docs.google.com/spreadsheets/d/1nGolhmva7qw7U_QwV3U7JTC9IhwMUMVbx5tSzGd3f14/export?format=csv")
surviveTraining = trainingSetDF.pop('Survived')

categoricalColumns = ['Race', 'Abilities', 'Weapons']
NumericColumns = ['Age', 'Level']

featureColumns = []

#creates features for training data to prepare it to load it into tensorflow
for feature_name in categoricalColumns:
  vocabulary = trainingSetDF[feature_name].unique()
  featureColumns.append(tf.feature_column.categorical_column_with_vocabulary_list(feature_name, vocabulary))

for feature_name in NumericColumns:
  featureColumns.append(tf.feature_column.numeric_column(feature_name, dtype=tf.float32))

#creates a function that takes information and shuffles the data and repeats it for the machine but not too many times to preamtively connect already seen information
def make_input_fn(data_df, label_df, num_epochs=10, shuffle=True, batch_size=32):
  def input_function():  
    ds = tf.data.Dataset.from_tensor_slices((dict(data_df), label_df)) 

    if shuffle:
      ds = ds.shuffle(1000)  

    ds = ds.batch(batch_size).repeat(num_epochs)
    return ds  

  return input_function

print("\nWelcome to character Custom character survivabilty thinga majig, we have created a machine that will guess how likely your custom built character will survive! \n")

#A while loop that allows the player to keep playing the game and creating characters until they chose to quit the game
while True:

  #Gives the player multiple promts to choose their characters atributes such as race, ability, and weapon type
  print("To get started, why not choose your characters race?")

  CCRace = [inquirer.List('Races', choices=['Elf', 'Dwarf', 'Undead', 'Human','Lizard', 'Giants', 'Centaur'])]
  raceAnswer = inquirer.prompt(CCRace)

  print("A " + raceAnswer['Races'] + " not a bad choice there son. Now what ability do you want to use? \n")

  CCAbility  = [inquirer.List('Abilities', choices=['Necromancy', 'Pyromancy', 'Warrior', 'Hydrophysist','Disney Princess'])]
  abilityAnswer = inquirer.prompt(CCAbility)

  print("A " + abilityAnswer['Abilities'] + " " + raceAnswer['Races'] + " I can't say I seen something like that, but you know, it might just work, or not I am not sure the computer dictates these things. \n")

  print("Alrighty, we're almost there, now we can't have you running off without some sort of weapon, there's plenty to choose from, why don't you take a look? \n")

  CCWeapons = [inquirer.List('Weapons', choices=['Wand', 'Duel Wielding', 'Two handed sword', 'Executioners Axe','Dagger', 'Mace'])]
  weaponsAnswer = inquirer.prompt(CCWeapons)

  print("Alrighty, it looks like we got a good start here folks! Now, the question is, can you survive? Of course you can, now go get em boy. Just one more thing, what do you want your name to be?")

  #Asks the user for a character name and then generates a random age, level and survivabilty(this will be used for the training will be popped out)
  CCName = input()
  CCLevel = random.randint(1,100)
  CCAge = random.randint(1,200)
  CCSurvived = random.randint(0,1)

  #creates a CSV to feed the machine of the users character
  row = [CCSurvived, raceAnswer['Races'], CCAge, abilityAnswer['Abilities'], weaponsAnswer['Weapons'], CCLevel, CCName]
  headerList = ["Survived", "Race", "Age", 'Abilities', 'Weapons', 'Level', 'Name']

  #writes to a local CSV created on users machine with header and the players stats
  with open('finalCSV', 'w') as evaluationFromCC:
      dw = csv.DictWriter(evaluationFromCC, delimiter=',', 
                          fieldnames=headerList)

      dw.writeheader()

      writer = csv.writer(evaluationFromCC)
      writer.writerow(row)

  evalDF = pd.read_csv('finalCSV')
  surviveEval = evalDF.pop('Survived')

  #this over here then trains the machine using the function I created above as well as then evalutes 
  trainInputFn = make_input_fn(trainingSetDF, surviveTraining)
  EvalInputFn = make_input_fn(evalDF, surviveEval, num_epochs=1, shuffle=False)

  linearEst = tf.estimator.LinearClassifier(feature_columns=featureColumns)
  linearEst.train(trainInputFn)

  #prints out the results, specificiliy the probabilty since theres multiple results the machine gives you
  results = linearEst.evaluate(EvalInputFn)

  results = list(linearEst.predict(EvalInputFn))

  #This then puts the characters stats into a SQL server thats online so that any user can see any characters the created previously
  for i in range(len(evalDF)):
    evalDF.loc[i, 'survived'] = results[i]['probabilities'][1]
    creatingTable(CCUsername, str(results[i]['probabilities'][1]), str(raceAnswer['Races']), str(CCAge), str(abilityAnswer['Abilities']), str(weaponsAnswer['Weapons']), str(CCLevel), CCName, 0)

  os.system('cls' if os.name == 'nt' else 'clear')

  print("Alrighty! ")
  print(evalDF)

  #Asks the players if they want to see their stats and if they want to try it again
  print("\nThat was a good try, do you want to see all your other previous attempts? \n")

  CCAll = [inquirer.List('All Characters', choices=['Yes', 'No'])]
  allCharactersAnswer = inquirer.prompt(CCAll)

  if allCharactersAnswer['All Characters'] == 'Yes':
    printDatabaseToScreen(CCUsername)

  print("Do you want to play again? \n")

  CCAgain = [inquirer.List('Play Again', choices=['Yes', 'No'])]
  playAgain = inquirer.prompt(CCAgain)

  if playAgain['Play Again'] == 'No':
    break

print("Thank you for playing!")