import mysql.connector,os
from pathlib import Path

# Connect to MySQL server
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='volara',
)

cursor = connection.cursor()
if cursor:
    print("successfully connected to database server.")
else:
    print("Could not connect to database!!! HUGE error occurred.")
    exit(404)

if os.path.exists("backup.sql") == True:

    with open("backup.sql", 'r', encoding='utf-8') as file:
        
        sql_code = file.read()
       
        cursor.execute(sql_code)
    
    os.remove("backup.sql")   
    
    print("backup rebuild executed successfully.")
    
else: 
    with open("tolls.sql", 'r', encoding='utf-8') as file:
        sql_code = file.read()
        cursor.execute(sql_code)
    
    print("SQL file executed as a total reset outside of a backup successfully.")

cursor.close()
connection.close()


