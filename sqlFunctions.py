#This file is the SQL functions that I import into the main file

import mysql.connector
from numpy.lib.shape_base import row_stack

#Estabilishes the connection with the server
databaseConnection = mysql.connector.connect(
    user='tbk4dsiq5e8ft3l6',
    password='x62gfa8rsi5clp80',
    host='kutnpvrhom7lki7u.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
    database='kpzf121fvx9a9dfg'
)

#creates a cursor used to use for the database
mycursor = databaseConnection.cursor()

#This will create the table, first it checks if the username already exists or not, if so then pushes information, if not creates info and then pushes the information into the table
def creatingTable(Username, Survived, Race, Age, Abilities, Weapons, Level, Name, usernameAlreadyExists):
    usernameAlreadyExists = 0

    query = ("show tables like '{}'".format(Username))
    mycursor.execute(query)

    for row in mycursor:
        new_lst=(','.join(row))     
        print("Welcome back: " + new_lst)
        usernameAlreadyExists = 1
        pushingInfo(Username, Survived, Race, Age, Abilities, Weapons, Level, Name)

    if(usernameAlreadyExists == 0):
        print("Creating new table ...")
        mycursor.execute("CREATE TABLE {} (Survived VARCHAR(10), Race VARCHAR(255), Age VARCHAR(25), Abilities VARCHAR(255), Weapons VARCHAR(255), Level VARCHAR(25), Name VARCHAR(255))".format(Username))
        pushingInfo(Username, Survived, Race, Age, Abilities, Weapons, Level, Name)

#Creates the functions that actually pushes the info 
def pushingInfo(Username, Survived, Race, Age, Abilities, Weapons, Level, Name):
    query = "INSERT INTO {} (Survived, Race, Age, Abilities, Weapons, Level, Name) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(Username)
    values = (Survived, Race, Age, Abilities, Weapons, Level, Name)
    mycursor.execute(query, values)
    databaseConnection.commit()
    print("success!")

#prints out the SQL table for the username associated to show the users previous results
def printDatabaseToScreen(username):
    query = 'SELECT * FROM {}'.format(username)
    mycursor.execute(query)
    
    myresults = mycursor.fetchall()

    for row in myresults:
        print(row)