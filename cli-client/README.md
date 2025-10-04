# CLI client

Ενδεικτικά περιεχόμενα:

- Command line interface (CLI).
- CLI functional tests.
- CLI unit tests.

This CLI tool provides various administrative and operational commands for managing toll station passes, analyzing pass data, and handling financial operations. It interacts with a backend server through a REST API.

# The API base URL is set to http://127.0.0.1:9115. Ensure your backend is running at this specific port (9115). 

**Installation and Usage**

1. Install dependancies:

`pip install typer requests`

2. Run install.bat in your windows pc

3. Run the CLI tool:

`se2437 <command> [options]`

**Commands**

1. System Initialization and Check

[healthcheck]: Checks the health of the system.

`se2437 healthcheck`

[resetstations]: Resets the tollstations and adds the ones from the tollstations2024.csv file.

`se2437 resetstations`

[resetpasses]: Resets the pass records and all the corresponding ones with the passes, like tags.

`se2437 resetpasses`

2. Data Import

[admin]: Adds passes records from a CSV file. Only admin has access.

`se2437 admin --addpasses --source <file_path>`

* --source (required): Path to the CSV file containing pass data.

3. Toll Station Operations

[tollstationpasses]: Retrieves toll station passes within a given date range.

`se2437 tollastationpasses --station <station_id> --from <YYYYMMDD> --to <YYYYMMDD> --format <json/csv>`

* --station (required): ID of the toll station.
* --from (required): Start date in YYYYMMDD format.
* --to (required): End date in YYYYMMDD format.
* --format (optional): Response format (default: json).

[passanalysis]: Analyzes passes between two operators.

`se2437 passanalysis --stationop <station_operator> --tagop <tag_operator> --from <YYYYMMDD> --to <YYYYMMDD> --format <json/csv>`

* --stationop (required): Station operator ID.
* --tagop (required): Tag operator ID.
* --from (required): Start date in YYYYMMDD format.
* --to (required): End date in YYYYMMDD format.
* --format (optional): Response format (default: json).

[passescost]: Retrieves the cost of passes between two operators.

`se2437 passescost --stationop <station_operator> --tagop <tag_operator> --from <YYYYMMDD> --to <YYYYMMDD> --format <json/csv>`

* Same parameters as passanalysis.

[chargesby]: Retrieves charges by an operator within a date range.

`se2437 chargesby --opid <operator_id> --from <YYYYMMDD> --to <YYYYMMDD> --format <json/csv>`

* --opid (required): Operator ID.
* --from (required): Start date in YYYYMMDD format.
* --to (required): End date in YYYYMMDD format.
* --format (optional): Response format (default: json).

[getDebts]: Retrieves the debts of a tag operator.

`se2437 getDebts --tagOpID <tag_operator_id> --format <json/csv>`

* --tagOpID (required): Tag operator ID.
* --format (optional): Response format (default: json).

[getProfits]: Retrieves profits of a tag operator.

`se2437 getProfits --tagOpID <tag_operator_id> --format <json/csv>`

* Same parameters as getDebts.

[getStatistics]: Retrieves statistics for a tag operator.

`se2437 getStatistics --tagOpID <tag_operator_id> --format <json/csv>`

* Same parameters as getDebts.


**TESTING FILE**

The file [test_cli.py] contains both CLI functional tests and CLI unit tests. 

# There are five CLI Functional Tests, three with subprocess tests and two with typer tests.

* def test_healthcheck_subprocess()
* def test_resetpasses_subprocess()
* def test_addpasses_subprocess()

* def test_healthcheck_typer()
* def test_resetpasses_typer()

# There are two CLI Unit Tests.

* def test_resetpasses_mock(mock_post)
* def test_healthcheck_mock(mock_get, capfd)

In order to run the tests, you chould type `pytest -v` inside the terminal (inside the path where the file exists).