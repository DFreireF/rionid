import pytest
import toml
import os
from rionid.importdata import ImportData

# Get the GitHub Actions workspace path
workspace_path = os.getenv('GITHUB_WORKSPACE')

# Construct the full path to the TOML file
toml_file_path = os.path.join(workspace_path, 'tests/test_importdata.toml')

# Load test data from TOML file
with open(toml_file_path, 'r') as toml_file:
    test_data = toml.load(toml_file)

@pytest.fixture(params=test_data['test_init'])
def import_data(request):
    # Parameterized fixture to create ImportData instances for each test case in the TOML file
    data = request.param
    return ImportData(data['ref_ion'], data['alphap'], data['csv_data'])

def test_initialization(import_data):
    """ Test the initialization of ImportData class. """
    assert import_data.ref_ion is not None
    assert import_data.alphap is not None
    assert import_data.ring is not None
    assert import_data.ref_charge is not None
    assert import_data.ref_aa is not None
