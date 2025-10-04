import csv
import io
import re
import json
import tempfile
import string,random
import mysql.connector  # import useful for connecting to our database
from flask import Flask, jsonify, request
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import config
import jwt
from flask_cors import CORS

DEBUG = False # enable/disable manually -> true is proposed for the time being

############################################## These two functions are used for technical reasons of the api endpoints / DO NOT CHANGE

def getTimestamp():
    timestamp_req = request.args.get('requestTimestamp')
    if timestamp_req is None:
        timestamp_req = datetime.now().strftime('%Y-%m-%d %H:%M')
    return timestamp_req

def format_date(date_str):
  """
  Converts a date string in YYYYMMDD format to YYYY-MM-DD HH:MM format.

  Args:
    date_str: The date string in YYYYMMDD format.

  Returns:
    The formatted date string in YYYY-MM-DD HH:MM format.
  """
  try:
    # Parse the input string into a datetime object and reformat into the desired
    date_obj = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')

    return date_obj
  
  except ValueError:
    return jsonify({"error": "Invalid date format. Dates should be in 'YYYYMMDD' format."}), 400

##############################################
def is_valid_date_format(date_string):
    """
    Checks if the date string is in the YYYYMMDD format and represents a valid date.

    :param date_string: The date string to check
    :return: True if the format is correct and the date is valid, False otherwise
    """
    # Regex to match YYYYMMDD format (exact 8 digits)
    if not re.fullmatch(r'\d{8}', date_string):
        return False

    try:
        # Try to convert to a valid date
        datetime.strptime(date_string, "%Y%m%d")
        return True
    except ValueError:
        return False

def generate_random_string(length=8):
  """Generates a random string of specified length."""

  characters = string.ascii_letters + string.digits  # Includes letters and digits
  random_string = ''.join(random.choice(characters) for _ in range(length))
  return random_string

# Generate a random string of length 8
random_string = generate_random_string()

app = Flask(__name__)
CORS(app)

# Predefined database configuration / might need to change these for your local database
db_config = {
    'user': 'root', #change this to your servers username
    'password': 'volara', #change this to your servers password
    'host': 'localhost', #change this to your servers host
    'database': 'toll_system'
}

@app.route('/admin/healthcheck', methods=['GET'])
def healthcheck():
    try:
        if DEBUG == True:
            print("healthcheck endpoint called")
        # Σύνδεση με την ΒΔ
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # number of stations currently stored
        cursor.execute("SELECT COUNT(*) FROM tollstations")
        n_stations = cursor.fetchone()[0]

        #number of tags currently used
        cursor.execute("SELECT COUNT(distinct tagRef) FROM passes")
        n_tags = cursor.fetchone()[0]

        #number of passes curently used
        cursor.execute("SELECT COUNT(*) FROM passes")
        n_passes = cursor.fetchone()[0]

        # Κλείσιμο σύνδεσης
        cursor.close()
        cnx.close()

        # Επιστροφή επιτυχίας
        response = {
            "status": "OK",
            "dbconnection": str(db_config),  # Απλοποιημένο connection string
            "n_stations": n_stations,
            "n_tags": n_tags,
            "n_passes": n_passes
        }
        
        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print(json.dumps(response))
            print("-----------------------")
        return json.dumps(response), 200

    except Exception as e:
        # Επιστροφή αποτυχίας
        response = {
            "status": "failed",
            "dbconnection": str(db_config)  # Απλοποιημένο connection string
        }
        
        if DEBUG == True:
            print("CRITICAL ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
            
        return json.dumps(response), 500

@app.route('/admin/resetstations', methods=['POST'])
def reset_stations():
  """
  Resets the toll stations table with data from the tollstations2024.csv file.

  Returns:
      json: A JSON object indicating success or failure.
  """
  if DEBUG == True:
        print("resetstations endpoint called")
        
  try:
    with open('tollstations2024.csv', 'r', encoding='utf-8') as file:
      reader = csv.reader(file)
      # Skip the header row if it exists
      next(reader, None)



      cnx = mysql.connector.connect(**db_config)
      cursor = cnx.cursor()
      # Clear existing data in the toll stations table (replace 'toll_stations' with your actual table name)
      cursor.execute("delete from tollstations")
      cursor.execute("delete from op_credentials")



      for row in reader:

        cursor.execute("Select count(*) from op_credentials where OpID = %s", (row[0],))

        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO op_credentials VALUES (%s, %s , %s)", (str(row[0]), str(row[1]) , str(row[9]) ))

        cursor.execute("INSERT INTO tollstations (OpID,Operator,TollID,Name,PM,Locality,Road,Lat,LONGG,Price1,Price2,Price3,Price4) VALUES (%s,%s,%s,%s,%s, %s, %s ,%s, %s, %s ,%s, %s, %s)",
                       (str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),str(row[6]),float(row[7]),float(row[8]),float(row[10]),float(row[11]),float(row[12]),float(row[13])))

      cnx.commit()
      
      if DEBUG == True:
        print("SUCCESS")
        print("-----------------------")
        print(json.dumps({"status": "OK"}))
        print("-----------------------")

    return json.dumps({"status": "OK"}), 200

  except Exception as e:
    if DEBUG == True:
        print("DANGEROUS ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")  
    return json.dumps({"status": "failed", "info": str(e)}), 500


@app.route('/admin/resetpasses', methods=['POST'])
def reset_passes():
    
    if DEBUG == True:
        print("reset_passes endpoint called")

    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()  # Assuming 'db' is your database connection
        cursor.execute("DELETE FROM passes;")
        cursor.execute("DELETE FROM ECONOMICS;")

        db.commit()
        
        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print(json.dumps({"status": "OK"}))
            print("-----------------------")
        return json.dumps({"status": "OK"}), 200

    except Exception as e:
        if DEBUG == True:
            print("critical error") # if this happens it needs investigation
        db.rollback()  # In case of error, rollback changes
        return json.dumps({"status": "failed", "info": str(e)}), 500

@app.route('/admin/addpasses', methods=['POST'])
def add_passes():
    if DEBUG == True:
        print("addpasses endpoint called")
    try:
        if ('file') not in request.files:
            if DEBUG == True:
                print("typical error in api request occured change postman please")
            return json.dumps({"status": "failed", "info": "No file part"}), 400

        csv_file = request.files['file']

        # The following may not be necessary ---------------------------------------------------------
        if csv_file.filename == '':
            if DEBUG == True:
                print("typical error in api request occured change postman please - NO FILE SELECTED")
            return json.dumps({"status": "failed", "info": "No selected file"}), 400
        # --------------------------------------------------------------------------------------------

        if not csv_file.filename.endswith('.csv'):
            if DEBUG == True:
                print("typical error in api request occured change postman please - INVALID FILE TYPE - CSV PLEASE")
            return json.dumps({"status": "failed", "info": "Invalid file type"}), 400

        # 2. File Handling (using tempfile for security)
        with tempfile.NamedTemporaryFile(delete=False) as temp_csv:
            csv_file.save(temp_csv.name)
            temp_csv_path = temp_csv.name

        # 3. CSV Parsing
        with open(temp_csv_path, 'r' ,encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)  # Use DictReader for easier access

            # 4. Database Operations
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor()

            for row in reader:

                while True:
                    code_ID = generate_random_string(8).upper()
                    cursor.execute("SELECT COUNT(*) from passes where passID = %s",(code_ID,))
                    if cursor.fetchone()[0] > 0:
                        continue
                    else:
                        break
                
                cursor.execute("INSERT  INTO passes (passID,timestamp,tagRef,tollID,tagHomeID,charge) VALUES (%s,%s,%s,%s,%s,%s)",(str(code_ID),str(row["timestamp"]),str(row["tagRef"]),str(row["tollID"]),str(row["tagHomeID"]),str(row["charge"]),))
            # Construct and execute SQL INSERT queries for 'passage_events' and related tables
            # ... (e.g., cursor.execute("INSERT INTO passage_events (column1, column2, ...) VALUES (%s, %s, ...)", (row['column1'], row['column2'], ...)))
            # ... (similarly for 'tags' or other dependent tables)

            db.commit()

        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print({"status": "OK"})
            print("-----------------------")

        return json.dumps({"status": "OK"}), 200

    except Exception as e:
        if DEBUG == True:
            print("DANGEROUS ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
        return json.dumps({"status": "failed", "info": str(e)}), 500


##########################################################



@app.route('/tollStationPasses/<string:tollStationID>/<string:date_from>/<string:date_to>', methods=['GET'])
def get_toll_station_passes(tollStationID, date_from, date_to):
  """
  Επιστρέφει αντικείμενο που περιέχει λίστα με την ανάλυση των
  διελεύσεων για τον σταθμό διοδίων και την περίοδο που δίνονται
  ως path parameters.
  """
  if DEBUG == True:
        print("tollStationPasses endpoint called")
  try:
    request_timestamp = getTimestamp()

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    

    format = request.args.get('format', 'json')

    date_from = date_from.strip()
    date_to = date_to.strip()

    # Ckeck whether we have the correct date format
    if not is_valid_date_format(date_from) or not is_valid_date_format(date_to):
        return jsonify({"error": "Invalid date format. Dates should be in 'YYYYMMDD' format."}), 400

    query = """
        SELECT (TollID) FROM tollstations WHERE TollID = %s
    """
    
    cursor.execute(query, (tollStationID,))
    ID_found = cursor.fetchall()
    
    if len(ID_found) == 0:
        return json.dumps({"error": "Invalid tollStationID."}), 400
    
    date_from = format_date(date_from)
    date_to = format_date(date_to)

    # First query to get the total number of passes
    query_count = """
        SELECT COALESCE(COUNT(*),0) 
        FROM passes  -- Replace with your actual table name
        WHERE tollID = %s AND timestamp>%s AND timestamp<%s
    """

    cursor.execute(query_count, (tollStationID, date_from, date_to,))
    count_result = cursor.fetchone()

    # Second query to get the details of each pass
    query_passes = """
        SELECT 
            passID, 
            timestamp, 
            tagRef, 
            tagHomeID, 
            passType, 
            charge 
        FROM passes  -- Replace with your actual table name
        WHERE tollID = %s AND timestamp>%s AND timestamp<%s
        ORDER BY timestamp ASC
    """
    
    cursor.execute(query_passes, (tollStationID, date_from, date_to,))
    passes_results = cursor.fetchall()


    passList = []
    for i, result in enumerate(passes_results):
      passList.append({
          "passIndex": i + 1,
          "passID": result[0],
          "timestamp": result[1],  # Format timestamp
          "tagID": result[2],
          "tagProvider": result[3],
          "passType": result[4],
          "passCharge": round(result[5], 2)  # Round to 2 decimal places
      })

    query = '''
    SELECT Operator
    FROM tollstations  
    where tollID = %s
    '''

    cursor.execute(query, (tollStationID,))
    station_operator= cursor.fetchall()
    

    response = {
        "stationID": tollStationID,  # Assuming this is the same as tollStationID
        "stationOperator": station_operator[0][0],  # Replace with how to get this value
        "requestTimestamp": request_timestamp,
        "periodFrom": date_from,
        "periodTo": date_to,
        "nPasses": len(passList),
        "passList": passList 
    }

    # If CSV format is requested, generate and return CSV data

    if format == 'csv':
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)

        # Write header row
        csv_writer.writerow(['stationID','stationOperator','requestTimestamp','periodFrom','periodTo','nPasses','passIndex','passID','timestamp','tagID','tagProvider','passType','passCharge'])

        i = 0
        for value in passList:

            if i==0:
                csv_writer.writerow([response["stationID"], response["stationOperator"],
                                     response["requestTimestamp"], response["periodFrom"], response["periodTo"],
                                     response["nPasses"],value['passIndex'],value['passID'],value['timestamp'],value['tagID'],value['tagProvider'],value['passType'],value['passCharge']])
            else:
                csv_writer.writerow(['','','','','','',value['passIndex'],value['passID'],value['timestamp'],value['tagID'],value['tagProvider'],value['passType'],value['passCharge']])

            i += 1


        # Get the CSV data as a string
        csv_output = csv_data.getvalue()

        # Set the content type to CSV
        headers = {'Content-Type': 'text/csv'}

        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print(csv_output)
            print("-----------------------")

        # Return the CSV data
        return csv_output, 200, headers

    else:
        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print(json.dumps(response))
            print("-----------------------")

        return json.dumps(response), 200, {'Content-Type': 'application/json'}

  except Exception as e:
    if DEBUG == True:
         print("CRITICAL ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
    return json.dumps({"error": str(e)}), 500
  

@app.route('/passAnalysis/<string:stationOpID>/<string:tagOpID>/<string:date_from>/<string:date_to>', methods=['GET'])
def pass_analysis(stationOpID, tagOpID, date_from, date_to):
    if DEBUG == True:
        print("passAnalysis endpoint called")
    
    try:
        # If stationOpID == "" or tagOpID == "", 404 NOT FOUND, else if the following, 400 BAD REQUEST
        if (stationOpID == " ") or (tagOpID == " ") or (date_from == None) or (date_to == None):
            return json.dumps({"error": "Missing required parameters."}), 400
        
        request_timestamp = getTimestamp()

        # Connect to the database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Connect to the database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        
    
        
        
        format = request.args.get('format', 'json')

        stationOpID = stationOpID.replace(":","")
        tagOpID = tagOpID.replace(":","")

        date_from = date_from.replace(":","")
        date_to = date_to.replace(":","")

        # Ckeck whether we have the correct date format
        if not is_valid_date_format(date_from) or not is_valid_date_format(date_to):
            return jsonify({"error": "Invalid date format. Dates should be in 'YYYYMMDD' format."}), 400


        query = """SELECT (OpID) FROM op_credentials WHERE OpID = %s """
    
        cursor.execute(query, (stationOpID,))
        ID_found = cursor.fetchall()
    
        if len(ID_found) == 0:
            return json.dumps({"error": "stationOpID does not exist."}), 400

        date_from = format_date(date_from)
        date_to = format_date(date_to)

        # SQL query (adapt to your database schema if needed)
        query = """
            SELECT 
                passID,
                tollID, 
                timestamp, 
                tagRef, 
                charge
            FROM passes 
            WHERE tagHomeID = %s AND LOCATE(%s,tollID)>0 AND timestamp>%s AND timestamp<%s
            ORDER BY timestamp ASC
            
        """

        # Execute the query
        cursor.execute(query, (stationOpID,tagOpID,date_from,date_to,))
        passes = cursor.fetchall()

        # Format the response
        response = {}
        response['stationOpID'] = stationOpID
        response['tagOpID'] = tagOpID
        response['requestTimestamp'] = request_timestamp 
        response['periodFrom']= date_from
        response['periodTo'] = date_to
        response['nPasses'] = len(passes)

        pass_list = []

        for i, pass_data in enumerate(passes):
            pass_list.append({
                'passIndex': i + 1,
                'passID': pass_data[0],
                'stationID': pass_data[1],
                'timestamp': pass_data[2],
                'tagID': pass_data[3],
                'passCharge': pass_data[4]
            })
        response['passList'] = pass_list

        if format == 'csv':
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)

            # Write header row
            csv_writer.writerow(['stationOpID','tagOpID','requestTimestamp','periodFrom','periodTo','nPasses','passIndex','passID','stationID','timestamp','tagID','passCharge'])

            i = 0
            for value in pass_list:

                if i == 0:
                    csv_writer.writerow([response["stationOpID"], response["tagOpID"],
                                         response["requestTimestamp"], response["periodFrom"], response["periodTo"],
                                         response["nPasses"], value['passIndex'], value['passID'], value['stationID'],
                                         value['timestamp'], value['tagID'], value['passCharge']])
                else:
                    csv_writer.writerow(['','','','','','', value['passIndex'], value['passID'], value['stationID'],
                                         value['timestamp'], value['tagID'], value['passCharge']])

                i += 1

            # Get the CSV data as a string
            csv_output = csv_data.getvalue()

            # Set the content type to CSV
            headers = {'Content-Type': 'text/csv'}
            
            if DEBUG == True:
                print("SUCCESS")
            
            # Return the CSV data
            return csv_output, 200, headers
            
        else:
            return json.dumps(response), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        if DEBUG == True:
            print("CRITICAL ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
        return jsonify({'error': str(e)}), 500


@app.route('/passesCost/<string:tollOpID>/<string:tagOpID>/<string:date_from>/<string:date_to>', methods=['GET'])
def get_passes_cost(tollOpID, tagOpID, date_from, date_to):
  """
  Υπολογίζει το κόστος διελεύσεων μεταξύ operators.

  Επιστρέφει αντικείμενο με τον αριθμό των γεγονότων διέλευσης που
  πραγματοποιήθηκαν με tag του tagOpID σε σταθμούς του tollOpID,
  καθώς και το κόστος τους, για τη δοσμένη περίοδο.
  """
  if DEBUG == True:
        print("passesCost endpoint called")
  
  try:
    # If tollOpID == "" or tagOpID == "", 404 NOT FOUND, else if the following, 400 BAD REQUEST
    if (tollOpID == " ") or (tagOpID == " ") or (date_from == None) or (date_to == None):
        return json.dumps({"error": "Missing required parameters."}), 400
        
    request_timestamp = getTimestamp()

    date_from = date_from.replace(":", "")
    date_to = date_to.replace(":", "")

    # Ckeck whether we have the correct date format
    if not is_valid_date_format(date_from) or not is_valid_date_format(date_to):
        return jsonify({"error": "Invalid date format. Dates should be in 'YYYYMMDD' format."}), 400

    date_from = format_date(date_from)
    date_to = format_date(date_to)


    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    query = """
        SELECT (OpID) FROM op_credentials WHERE OpID = %s
        """
    
    cursor.execute(query, (tollOpID,))
    ID_found = cursor.fetchall()
    
    if len(ID_found) == 0:
        return json.dumps({"error": "tollOpID does not exist."}), 400
    
    cursor.execute(query, (tagOpID,))
    ID_found = cursor.fetchall()
    
    if len(ID_found) == 0:
        return json.dumps({"error": "tagOpID does not exist."}), 400

    format = request.args.get('format', 'json')

    query = """
        SELECT 
            COALESCE(COUNT(*),0), 
            COALESCE(SUM(charge),0)
        FROM 
            passes  
        WHERE 
            LOCATE(%s,tollID)>0
            AND tagHomeID = %s 
            AND timestamp>%s 
            AND timestamp<%s
    """
    cursor.execute(query, (tollOpID, tagOpID, date_from, date_to,))
    result = cursor.fetchone()

    if result:
      response = {
          "tollOpID": tollOpID,
          "tagOpID": tagOpID,
          "requestTimestamp": request_timestamp,
          "periodFrom": date_from,
          "periodTo": date_to,
          "nPasses": result[0],
          "passesCost": round(result[1],2)
      }
    else:
      response = {
          "tollOpID": tollOpID,
          "tagOpID": tagOpID,
          "requestTimestamp": request_timestamp,
          "periodFrom": date_from,
          "periodTo": date_to,
          "nPasses": 0,
          "passesCost": 0.00
      }

    # Check if CSV format is requested
    if format == 'csv':
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)


        # Write header row
        csv_writer.writerow(["tollOpID","tagOpID","requestTimestamp","periodFrom","periodTo","nPasses","passesCost"])
        csv_writer.writerow([response["tollOpID"], response["tagOpID"],response["requestTimestamp"],response["periodFrom"],response["periodTo"],response["nPasses"],response["passesCost"]])


        # Get the CSV data as a string
        csv_output = csv_data.getvalue()

        # Set the content type to CSV
        headers = {'Content-Type': 'text/csv'}
        if DEBUG == True:
            print("SUCCESS")

        # Return the CSV data
        return csv_output, 200, headers
    else:
        if DEBUG == True:
            print("SUCCESS")
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

  except Exception as e:
    if DEBUG == True:
        print("CRITICAL ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
    return json.dumps({"error": str(e)}), 500


@app.route('/chargesBy/<string:tollOpID>/<string:date_from>/<string:date_to>', methods=['GET'])
def get_charges_by(tollOpID, date_from, date_to):
  """
  Επιστρέφει λίστα με τον αριθμό των γεγονότων διέλευσης και το κόστος τους
  για κάθε visiting operator σε σταθμούς του tollOpID, για τη δοσμένη περίοδο.
  """
  if DEBUG == True:
        print("chargesBy endpoint called")
  try:
    
    
    request_timestamp = getTimestamp()

    date_from = date_from.replace(":", "")
    date_to = date_to.replace(":", "")

    # Ckeck whether we have the correct date format
    if not is_valid_date_format(date_from) or not is_valid_date_format(date_to):
        return jsonify({"error": "Invalid date format. Dates should be in 'YYYYMMDD' format."}), 400

    date_from = format_date(date_from)
    date_to = format_date(date_to)

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    query = """
    SELECT (OpID) FROM op_credentials WHERE OpID = %s
        """
    
    cursor.execute(query, (tollOpID,))
    ID_found = cursor.fetchall()
    
    if len(ID_found) == 0:
        return json.dumps({"error": "tollOpID does not exist."}), 400

    format = request.args.get('format', 'json')

    query = """
        SELECT 
            tagHomeID, 
            COALESCE(COUNT(*),0), 
            COALESCE(SUM(charge),0)   
        FROM 
            passes  
        WHERE 
            LOCATE(%s,tollID)>0
            AND tagHomeID != %s 
            AND timestamp>%s 
            AND timestamp<%s  
        GROUP BY 
            tagHomeID
    """
    cursor.execute(query, (tollOpID,tollOpID,date_from,date_to))
    results = cursor.fetchall()

    vOpList = []
    for result in results:
      vOpList.append({
          "visitingOpID": result[0],
          "nPasses": result[1],
          "passesCost": round(result[2], 2)  # Round to 2 decimal places
      })

    response = {
        "tollOpID": tollOpID,
        "requestTimestamp": request_timestamp,
        "periodFrom": date_from,
        "periodTo": date_to,
        "vOpList": vOpList
    }
    if format == 'csv':
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)

        # Write header row
        csv_writer.writerow(["tollOpID","requestTimestamp","periodFrom","periodTo","visitingOpID","nPasses","passesCost"])

        i = 0
        for value in vOpList:

            if i == 0:
                csv_writer.writerow([response["tollOpID"], response["requestTimestamp"],
                                     response["periodFrom"], response["periodTo"],
                                     value["visitingOpID"], value['nPasses'], value['passesCost']])
            else:
                csv_writer.writerow(['', '', '', '', value["visitingOpID"], value['nPasses'], value['passesCost']])

            i += 1

        # Get the CSV data as a string
        csv_output = csv_data.getvalue()

        # Set the content type to CSV
        headers = {'Content-Type': 'text/csv'}
        if DEBUG == True:
            print("SUCCESS")
        # Return the CSV data
        return csv_output, 200, headers

    else:
        if DEBUG == True:
            print("SUCCESS")
            print("-----------------------")
            print(json.dumps(response))
            print("-----------------------")
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

  except Exception as e:
    if DEBUG == True:
        print("CRITICAL ERROR - IF OCCURED REQUIRES FURTHER INVESTIGATION")
    return json.dumps({"error": str(e)}), 500


#Display debts of the connected operator towards the all the others
@app.route('/ShowDebts/<string:tagOpID>', methods=['GET'])
def get_debts(tagOpID):
    try:
        # If tagOpID == "", 404 NOT FOUND, else if the following, 400 BAD REQUEST
        if (tagOpID == " "):
            return json.dumps({"error": "Missing required parameter."}), 400
    
        request_timestamp = getTimestamp()

        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        format = request.args.get('format', 'json')
        query = """
            SELECT 
                related_opID,
                amount   -- AS total_charge
            FROM 
                Economics  
            WHERE 
                OpID = %s AND relation = '-'
        """

        cursor.execute(query, (tagOpID,))
        results = cursor.fetchall()
       

        DebtsList = []
        for result in results:
            debt_operator = result[0] if result[0] is not None else "NULL"
            charge = result[1] if result[1] is not None else "0.0"
            DebtsList.append({
                "owned_operator": debt_operator,
                "charge": charge
            })

        response = {
            "tagOpID": tagOpID,
            # "requestTimestamp": request_timestamp,
            "DebtsList": DebtsList
        }


        if format == 'csv':
            print("entered")
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)

            # Write header row
            csv_writer.writerow(
                ["tagOpID", "owned_operator", "charge"])

            i = 0
            for value in DebtsList:

                if i == 0:
                    csv_writer.writerow([response["tagOpID"],
                                         value["owned_operator"], value['charge']])
                else:
                    csv_writer.writerow(['', value["owned_operator"], value['charge']])

                i += 1

            # Get the CSV data as a string
            csv_output = csv_data.getvalue()

            # Set the content type to CSV
            headers = {'Content-Type': 'text/csv'}
            if DEBUG == True:
                print("SUCCESS")
            # Return the CSV data
            return csv_output, 200, headers
        else:
            if DEBUG == True:
                print("SUCCESS")
            print(response)
            return json.dumps(response), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return json.dumps({"error": str(e)}), 500

#Display debts of the connected operator towards the all the others
@app.route('/ShowProfits/<string:tagOpID>', methods=['GET'])
def get_profits(tagOpID):
    try:
        # If tagOpID == "", 404 NOT FOUND, else if the following, 400 BAD REQUEST
        if (tagOpID == " "):
            return json.dumps({"error": "Missing required parameter."}), 400
        
        request_timestamp = getTimestamp()

        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        format = request.args.get('format', 'json')
        query2 = """
                    SELECT 
                        related_opID,
                        amount   -- AS total_charge
                    FROM 
                        Economics  
                    WHERE 
                        OpID = %s AND relation = '+'
              """

        cursor.execute(query2, (tagOpID,))
        results2 = cursor.fetchall()
        

        ProfitsList = []
        for result2 in results2:
            debt_operator = result2[0] if result2[0] is not None else "NULL"
            charge2 = result2[1] if result2[1] is not None else "0.0"
            ProfitsList.append({
                "debt_operator": debt_operator,
                "charge2": charge2
            })

        response2 = {
            "tagOpID": tagOpID,
            "DebtsList": ProfitsList
        }


        if format == 'csv':
            print("entered")
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)

            # Write header row
            csv_writer.writerow(
                ["tagOpID", "debt_operator", "charge2"])

            i = 0
            for value2 in ProfitsList:

                if i == 0:
                    csv_writer.writerow([response2["tagOpID"],
                                        value2["debt_operator"], value2["charge2"]])
                else:
                    csv_writer.writerow(
                        ['', value2["debt_operator"], value2["charge2"]])

                i += 1

            # Get the CSV data as a string
            csv_output = csv_data.getvalue()

            # Set the content type to CSV
            headers = {'Content-Type': 'text/csv'}
            if DEBUG == True:
                print("SUCCESS")
            # Return the CSV data
            return csv_output, 200, headers
        else:
            if DEBUG == True:
                print("SUCCESS")
                print("-----------------------")
                print(json.dumps(response2))
                print("-----------------------")
            return json.dumps(response2), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return json.dumps({"error": str(e)}), 500


@app.route('/ShowStatistics/<string:tagOpID>', methods=['GET'])
def get_statistics(tagOpID):
    try:
        # If tagOpID == "", 404 NOT FOUND, else if the following, 400 BAD REQUEST
        if (tagOpID == " "):
            return json.dumps({"error": "Missing required parameter."}), 400
        
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        format = request.args.get('format', 'json')
        query = """
                SELECT 
                    p1.tagHomeID, 
                    p1.operator_passer, 
                    COUNT(*) as connection_count,
                    ROUND( (COUNT(*) / total.total_connections) * 100, 2) as percentage
                FROM Passes p1
                JOIN (
                    SELECT tagHomeID, COUNT(*) as total_connections
                    FROM Passes
                    WHERE tagHomeID = %s
                    GROUP BY tagHomeID
                ) total
                ON p1.tagHomeID = total.tagHomeID
                WHERE p1.tagHomeID = %s
                GROUP BY p1.tagHomeID, p1.operator_passer, total.total_connections
                ORDER BY connection_count DESC;
              """

        cursor.execute(query, (tagOpID,tagOpID,))
        results = cursor.fetchall()

        StatisticsList = []
        for result in results:
            StatisticsList.append({
                "tagHomeID": result[0],
                "operator_passer": result[1],
                "connection_count": int(result[2]),
                "percentage": float(result[3])
            })

        response2 = {
            "tagOpID": tagOpID,
            "DebtsList": StatisticsList
        }

        if format == 'csv':
            print("entered")
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)

            # Write header row
            csv_writer.writerow(
                ["tagOpID", "operator_passer", "connection_count", "percentage"])

            i = 0
            for value2 in StatisticsList:

                if i == 0:
                    csv_writer.writerow([response2["tagOpID"],
                                         value2["operator_passer"], value2["connection_count"], value2["percentage"]])
                else:
                    csv_writer.writerow(
                        ['', value2["operator_passer"],value2["connection_count"], value2["percentage"]])

                i += 1

            # Get the CSV data as a string
            csv_output = csv_data.getvalue()

            # Set the content type to CSV
            headers = {'Content-Type': 'text/csv'}
            if DEBUG == True:
                print("SUCCESS")
            # Return the CSV data
            return csv_output, 200, headers
        else:
            if DEBUG == True:
                print("SUCCESS")
                print("-----------------------")
                print(json.dumps(response2))
                print("-----------------------")
            return json.dumps(response2), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return json.dumps({"error": str(e)}), 500


if __name__ == '__main__':
    print("Initializing the API")
    app.run(host='0.0.0.0', debug=True, port = 9115)