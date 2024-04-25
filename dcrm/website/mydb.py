import mysql.connector

dataBase = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'pakistan47',
)

#prepare cursor object

cursorObject = dataBase.cursor()

#create a database
cursorObject.execute("Create DATABASE easyhandover")

print("Database created! All Done!")