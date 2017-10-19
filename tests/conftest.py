import pytest
import yaml
import stl_path
from trex_stl_lib.api import *


def pytest_addoption(parser):
    parser.addoption("--config", action="store",
                     help="Configuration file")


def pytest_configure(config):

    filename = config.getoption("--config")
    with open(filename) as f:
        config.yaml_cfg = yaml.load(f.read())


@pytest.fixture(scope='session')
def trex(request):
    # verbose_level = LoggerApi.VERBOSE_HIGH
    server = request.config.yaml_cfg['trex']['server']
    my_ports = request.config.yaml_cfg['trex']['ports']
    c = STLClient(server=server)
    # connect to server
    c.connect()
    # prepare our ports
    c.reset(ports=my_ports)

    def tearDown():
        c.stop()
        c.remove_all_captures()
        c.set_service_mode(enabled=False)
        c.disconnect()

    request.addfinalizer(tearDown)
    return c
