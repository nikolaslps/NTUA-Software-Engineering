import time,mysql.connector

backup = "backup.sql"

db_config = {
    'user': 'root', #change this to your servers username
    'password': 'volara', #change this to your servers password
    'host': 'localhost', #change this to your servers host
    'database': 'toll_system'
}

connection_bridge = mysql.connector.connect(**db_config)
cursor = connection_bridge.cursor()





with open(backup, 'w') as file:
    file.write("""
DROP DATABASE IF EXISTS toll_system;
CREATE DATABASE toll_system;
USE toll_system;

CREATE TABLE Op_Credentials (
    OpID VARCHAR(8) PRIMARY KEY,
    Operator VARCHAR(20),
    email VARCHAR(40)
);

CREATE TABLE TollStations (
    OpID VARCHAR(8),
    Operator VARCHAR(40),
    TollID VARCHAR(8) PRIMARY KEY,
    Name VARCHAR(90),
    PM VARCHAR(6),
    Locality VARCHAR(30),
    Road VARCHAR(40),
    Lat FLOAT(7),
    LONGG FLOAT(7),
    Price1 FLOAT(4),
    Price2 FLOAT(4),
    Price3 FLOAT(4),
    Price4 FLOAT(4)

);

CREATE TABLE Passes (
    passID VARCHAR(8),
    timestamp VARCHAR(40),
    tagRef VARCHAR(10) ,
    tollID VARCHAR(20),
    tagHomeID VARCHAR(8),
    charge FLOAT(4),
    passType VARCHAR(10),
    operator_passer VARCHAR(8),
    PRIMARY KEY (passID)
);




CREATE TABLE Economics (
    OpID VARCHAR(8),
    related_opID VARCHAR(8),
    amount FLOAT(15),
    relation CHAR(1) CHECK (relation IN ('+', '-')),
    PRIMARY KEY (OpID, related_opID),
    FOREIGN KEY (OpID) REFERENCES Op_Credentials(OpID),
    FOREIGN KEY (related_opID) REFERENCES Op_Credentials(OpID)
);

\n"""
)#inside this is the script that creates the tables of the database



time.sleep(0.5)
print("Backup script for basic tables build was generated successfully.")
time.sleep(0.5)
print("adding the insertion of the data now...")
time.sleep(0.5)


print("pulling and writing necessary build data and Formatting it accordingly...")
time.sleep(0.5)

    
    
    
#############################################################
cursor.execute("SELECT * FROM op_credentials")
data = cursor.fetchall()
if len(data) > 0:
    open(backup,'a',encoding='utf-8').write("Insert into op_credentials values ")
    for i,item in enumerate(data):
        if i == len(data)-1:
            open(backup,'a',encoding='utf-8').write(f"{item};\n")
        else:
            open(backup,'a',encoding='utf-8').write(f"{item},")
#############################################################
cursor.execute("SELECT * FROM economics")
data = cursor.fetchall()
if len(data) > 0:
    open(backup,'a',encoding='utf-8').write("Insert into economics values\n")
    for i,item in enumerate(data):
        if i == len(data)-1:
            open(backup,'a',encoding='utf-8').write(f"{item};\n")
        else:
            open(backup,'a',encoding='utf-8').write(f"{item},")
#############################################################
#cursor.execute("SELECT * FROM login")
#data = cursor.fetchall()
#if len(data) > 0:
#    open(backup,'a',encoding='utf-8').write("Insert into login values\n")
#    for i,item in enumerate(data):
#        if i == len(data)-1:
#            open(backup,'a',encoding='utf-8').write(f"{item};\n")
#        else:
#            open(backup,'a',encoding='utf-8').write(f"{item},")
#############################################################
cursor.execute("SELECT * FROM tollstations")
data = cursor.fetchall()
if len(data) > 0:
    open(backup,'a',encoding='utf-8').write("Insert into tollstations values\n")
    for i,item in enumerate(data):
        if i == len(data)-1:
            open(backup,'a',encoding='utf-8').write(f"{item};\n")
        else:
            open(backup,'a',encoding='utf-8').write(f"{item},")
#############################################################
cursor.execute("SELECT * FROM passes")
data = cursor.fetchall()
if len(data) > 0:
    open(backup,'a',encoding='utf-8').write("Insert into passes values\n")
    for i,item in enumerate(data):
        if i == len(data)-1:
            open(backup,'a',encoding='utf-8').write(f"{item};\n")
        else:
            open(backup,'a',encoding='utf-8').write(f"{item},")
#############################################################

print("Task done")
time.sleep(1)
print("Now write triggers script")
time.sleep(1)

with open(backup, 'a') as file:
    file.write("""\n

CREATE TRIGGER pass_type_entrance
BEFORE INSERT
ON passes
FOR EACH ROW
BEGIN

    IF LOCATE(NEW.tagHomeID,NEW.tollID)>0
    THEN
        SET NEW.passType = 'home';
    ELSE
        SET NEW.passType = 'visitor';

    END IF;
    -- SQL statements to be executed before insert
END;




CREATE TRIGGER insert_relations_debt
AFTER INSERT
ON Passes
FOR EACH ROW
BEGIN
    DECLARE toll_operator VARCHAR(8);

    IF NEW.passType = 'visitor' THEN
        SELECT OpID INTO toll_operator
        FROM TollStations
        WHERE TollID = NEW.tollID;


        IF toll_operator IS NOT NULL AND
           EXISTS (SELECT 1 FROM Op_Credentials WHERE OpID = NEW.tagHomeID) AND
           EXISTS (SELECT 1 FROM Op_Credentials WHERE OpID = toll_operator) THEN


            IF EXISTS (SELECT 1 FROM Economics WHERE OpID = NEW.tagHomeID AND related_opID = toll_operator) THEN
                UPDATE Economics
                SET amount = amount + NEW.charge
                WHERE OpID = NEW.tagHomeID AND related_opID = toll_operator;
            ELSE
                INSERT INTO Economics (OpID, related_opID, amount, relation)
                VALUES (NEW.tagHomeID, toll_operator, NEW.charge, '-');
            END IF;

            IF EXISTS (SELECT 1 FROM Economics WHERE OpID = toll_operator AND related_opID = NEW.tagHomeID) THEN
                UPDATE Economics
                SET amount = amount + NEW.charge
                WHERE OpID = toll_operator AND related_opID = NEW.tagHomeID;
            ELSE
                INSERT INTO Economics (OpID, related_opID, amount, relation)
                VALUES (toll_operator, NEW.tagHomeID, NEW.charge, '+');
            END IF;

        END IF;
    END IF;

END;



CREATE TRIGGER insert_name_operator_passer
BEFORE INSERT
ON Passes
FOR EACH ROW
BEGIN
    DECLARE toll_operator VARCHAR(8);

    SELECT OpID INTO toll_operator
    FROM TollStations
    WHERE TollID = NEW.tollID;

    SET NEW.operator_passer = toll_operator;

END;

""")
    
print("Triggers script generated successfully.")
print("Success")

connection_bridge.close()