import subprocess
import json
import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from cli import app  # Ensure cli.py uses Typer

runner = CliRunner()

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    return result.stdout.strip()

### Helper Function ###
def run_command(command):
    """Runs a shell command and returns output."""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

### 1. Subprocess Tests (Real Execution) ###
def test_healthcheck_subprocess():
    output = run_command("python cli.py healthcheck")
    assert "status" in output  # Adjust based on actual response

def test_resetpasses_subprocess():
    output = run_command("python cli.py resetpasses")
    assert "OK" in output  # Expected API response

def test_addpasses_subprocess():
    output = run_command('python cli.py admin --addpasses --source "passes-sample.csv"')
    assert "Passes added successfully." in output

### 2. Typer CLI Tests ###
def test_healthcheck_typer():
    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 0
    assert "status" in result.output  # Adjust based on actual response

def test_resetpasses_typer():
    result = runner.invoke(app, ["resetpasses"])
    assert result.exit_code == 0
    assert "OK" in result.output

### 3. Mock API Response Tests ###
@patch("requests.post")
def test_resetpasses_mock(mock_post):
    mock_post.return_value.json.return_value = {"message": "success"}
    mock_post.return_value.status_code = 200

    from cli import resetpasses
    resetpasses()  # Call the function, should use the mocked response

import pytest
from unittest.mock import patch
from cli import healthcheck  # Import the function you are testing

@patch("requests.get")
def test_healthcheck_mock(mock_get, capfd):
    """Test healthcheck API using a mocked request."""

    # Mock the GET request response
    mock_get.return_value.json.return_value = {"status": "OK"}  # Mock API Response
    mock_get.return_value.status_code = 200  # Mock Status Code

    healthcheck()

    # Capture printed output
    captured = capfd.readouterr()

    assert "{'status': 'OK'}" in captured.out  # Check printed output


### Run tests using: `pytest test_cli.py` ###
