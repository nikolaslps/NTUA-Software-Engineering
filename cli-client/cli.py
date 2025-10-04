import typer
import requests
from typing import Optional

app = typer.Typer()

# Base URL for the API (update as necessary)
BASE_URL = "http://127.0.0.1:9115"  # Assuming Flask app is running locally


def validate_format(format: str):
    """Validate the format parameter."""
    valid_formats = ["json", "csv"]
    if format not in valid_formats:
        typer.echo(f"Invalid format '{format}'. Valid formats are 'json' or 'csv'.")
        raise typer.Exit(1)


# System Initialization & Check
@app.command()
def resetpasses():
    """Reset the passes."""
    url = f"{BASE_URL}/admin/resetpasses"
    response = requests.post(url, verify=False)  # Disable SSL verification for local testing
    typer.echo(f"{response.json()}")


@app.command()
def resetstations():
    """Reset the toll stations."""
    url = f"{BASE_URL}/admin/resetstations"
    response = requests.post(url, verify=False)
    typer.echo(f"{response.json()}")


@app.command()
def healthcheck():
    """Check the health of the system."""
    url = f"{BASE_URL}/admin/healthcheck"
    response = requests.get(url, verify=False)
    typer.echo(f"{response.json()}")


# Data Import
@app.command()
def admin(
    addpasses: bool = typer.Option(False, "--addpasses", help="Add passes from a CSV file"),
    source: str = typer.Option(None, "--source", help="Source File")
):
    """Admin command group with addpasses option."""
    if addpasses:
        if not source:
            typer.echo("Error: --source is required when using --addpasses")
            raise typer.Exit(1)

        url = f"{BASE_URL}/admin/addpasses"
        with open(source, 'rb') as file:
            files = {'file': (source, file, 'text/csv')}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            typer.echo("Passes added successfully.")
        else:
            typer.echo(f"Failed to add passes: {response.status_code}, {response.text}")
    else:
        typer.echo("No valid admin action provided. Use --addpasses.")


# Toll Station Operations
@app.command()
def tollstationpasses(
        station: str = typer.Option(...,  "--station", help="Station"),
        from_date: str = typer.Option(..., "--from", help="Start date (YYYYMMDD)"),  # Start Date
        to_date: str = typer.Option(..., "--to", help="End date (YYYYMMDD)"),  # End Date
        format: str = typer.Option("json", "--format", help="Response format (default: json)")
    ):
    """Get toll station passes within the given date range."""
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/tollStationPasses/{station}/{from_date}/{to_date}?format={format}"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Toll station passes (JSON): {response.json()}")
            elif format == "csv":
                typer.echo(f"Toll station passes (CSV):\n{response.text}")
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Failed to fetch toll station passes: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")




@app.command()
def passanalysis(
        stationop: str = typer.Option(..., "--stationop", help="Station Operator"),
        tagop: str = typer.Option(..., "--tagop", help="Tag Operator"),
        from_date: str = typer.Option(..., "--from", help="Start date (YYYYMMDD)"),  # Start Date
        to_date: str = typer.Option(..., "--to", help="End date (YYYYMMDD)"),  # End Date
        format: str = typer.Option("json", "--format", help="Response format (default: json)")
    ):
    """Get pass analysis between two operators."""
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/passAnalysis/{stationop}/{tagop}/{from_date}/{to_date}?format={format}"
    try:
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Pass analysis (JSON): {response.json()}")
            elif format == "csv":
                typer.echo(f"Pass analysis (CSV):\n{response.text}")
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Failed to fetch pass analysis: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")



@app.command()
def passescost(
        stationop: str = typer.Option(..., "--stationop", help="Station Operator"),
        tagop: str = typer.Option(..., "--tagop", help="Tag Operator"),
        from_date: str = typer.Option(..., "--from", help="Start date (YYYYMMDD)"),  # Start Date
        to_date: str = typer.Option(..., "--to", help="End date (YYYYMMDD)"),  # End Date
        format: str = typer.Option("json", "--format", help="Response format (default: json)")
    ):
    """Get passes cost between two operators."""
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/passesCost/{stationop}/{tagop}/{from_date}/{to_date}?format={format}"
    try:
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Passes cost (JSON): {response.json()}")
            elif format == "csv":
                typer.echo(f"Passes cost (CSV):\n{response.text}")
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Failed to fetch passes cost: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")



@app.command()
def chargesby(
    opid: str = typer.Option(..., "--opid", help="Operator ID"),
    from_date: str = typer.Option(..., "--from", help="Start date (YYYYMMDD)"),
    to_date: str = typer.Option(..., "--to", help="End date (YYYYMMDD)"),
    format: str = typer.Option("json", "--format", help="Response format: 'json' or 'csv' (default: 'json')")
):
    """
    Get charges by operator within the specified date range.
    """
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/chargesBy/{opid}/{from_date}/{to_date}?format={format}"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Charges by operator (JSON): {response.json()}")
            elif format == "csv":
                typer.echo(f"Charges by operator (CSV):\n{response.text}")
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")



@app.command()
def getDebts(
    tagOpID: str = typer.Option(..., "--tagOpID", help="Tag Operator ID"),
    format: str = typer.Option("json", "--format", help="Response format: 'json' or 'csv' (default: 'json')")
):

    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/ShowDebts/{tagOpID}?format={format}"
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            # Handle JSON response
            if format == "json":
                typer.echo(f"Debts (JSON): {response.json()}")
            # Handle CSV response
            elif format == "csv":
                typer.echo("Debts (CSV):")
                typer.echo(response.text)
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")


@app.command()
def getProfits( tagOpID: str = typer.Option(..., "--tagOpID", help="Tag Operator ID"),
    format: str = typer.Option("json", "--format", help="Response format: 'json' or 'csv' (default: 'json')")
):
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/ShowProfits/{tagOpID}?format={format}"
    try:
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Profits (JSON): {response.json()}")
            elif format == "csv":
                typer.echo("Profits (CSV):")
                typer.echo(response.text)
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")


@app.command()
def getStaistics( tagOpID: str = typer.Option(..., "--tagOpID", help="Tag Operator ID"),
    format: str = typer.Option("json", "--format", help="Response format: 'json' or 'csv' (default: 'json')")
):
    validate_format(format)  # Validate the format

    url = f"{BASE_URL}/ShowProfits/{tagOpID}?format={format}"
    try:
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            if format == "json":
                typer.echo(f"Statistics (JSON): {response.json()}")
            elif format == "csv":
                typer.echo("Statistics (CSV):")
                typer.echo(response.text)
            else:
                typer.echo("Unsupported format specified.")
        else:
            typer.echo(f"Error: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Request failed: {e}")


if __name__ == "__main__":
    app()
