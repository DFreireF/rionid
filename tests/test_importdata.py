import pytest
import toml
from rionid import ImportData

# Load test data from TOML file
with open('test_importdata.toml', 'r') as toml_file:
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
    