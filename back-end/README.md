# Back-end





Eνδεικτικά περιεχόμενα:

- Πηγαίος κώδικας εφαρμογής για εισαγωγή, διαχείριση και
  πρόσβαση σε δεδομένα (backend).
- Database dump (sql ή json)
- Back-end functional tests.
- Back-end unit tests.
- RESTful API.

**Database Configuration and Connection**
```bash
user='your_server_name' # Change this to your servers username
password='your_server_password' # Change this to your servers' password
host='localhost'
database='toll_system' 
port=9115
DEBUG=True OR False # True for printing massages for Debbugging, False for ignoring them
```

**Steps to first run**
-open terminal and file Api_main
-Generally type in terminal pip install <> where <> is the different python libraries
-Download mysql community version
-set up your server
-From now on insert your servers credentials into the following files of the folder Backend
-Please run the db_builder.py. This will set up the database.
-now run the API_main.py 
-install postman 
-import postman file
-select for dummy data to insert through passes37 or samples-passes37
-add dummy data to addpasses endpoint in passes
-Now you have your own server with our database 
-you can run api endpoints as long as the Api_main.py runs in your pc
-you need to go to frontend section if u want to see our frontend , but please let the API keep running


