import pytest

from redfish_lab.api import make_api
from redfish_lab.runtime import LabRegistry


@pytest.fixture
def lab():
    registry = LabRegistry()
    make_api(registry, background=False)
    session = registry.new()
    yield registry, session
    registry.close()
