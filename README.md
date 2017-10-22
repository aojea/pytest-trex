# Using trex with pytest to test network devices

For testing network devices it's common to use scapy, but this approach has
typcally 2 main problems:

* Handling the sending - receiving packet logic
* Lack of abstraction of the infraestructure

Using pytest with TREX API we can run our tests overcoming those problems. 
It also permit us to run tests in parallel on different devices

## Demostration

**It's turned out that the TREX api code that's in the repo doesn't work in MAC
by default**

The Vagrantfile deploys us the typical DUT infraestructure:





                +-----------------------+
                |                       |
                |                       |
       +--------+     DUT               +---------+
       |        |                       |         |
       |        |                       |         |
       |        |                       |         |
       |        +-----------------------+         |
       |                                          |
       |                                          |
       |                                          |
       |                                          |
       |                                          |
       |                                          |
       |         +----------------------+         |
       |         |                      |         |
       |         |                      |         |
       |         |                      |         |
       +---------+       T-Rex          +---------+
                 |       (Test device)  |
                 |                      |
                 +----------------------+


We can use the --config option to select the IP of the trex server and leverage
T-Rex to handle the sending receiving packet logic permitting us to focus only
in the testing scenarios. 

The following code in the conftest.py file handle the --config option:

```python
def pytest_addoption(parser):
    parser.addoption("--config", action="store",
                     help="Configuration file")


def pytest_configure(config):

    filename = config.getoption("--config")
    with open(filename) as f:
        config.yaml_cfg = yaml.load(f.read())

```

We can use a fixture ( [check the pytest documentation if you don't know what is
this](https://docs.pytest.org/en/latest/fixture.html) ) to connect to the Trex
API server and pass it to the tests:

```python
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
```

We need to configure the mac addresses of the interfaces and add static arp
entries in the DUT. The Vagrantfile use static mac address and automatically
configure Trex to use them, in the DUT we need to configure it manually:

```
root@vsrx# show interfaces 
ge-0/0/0 {
    unit 0 {
        family inet {
            dhcp;
        }
    }
}
ge-0/0/1 {
    unit 0 {
        family inet {
            address 192.168.50.5/24 {
                arp 192.168.50.4 mac 08:00:27:11:22:01;
            }
        }
    }
}
ge-0/0/2 {
    unit 0 {
        family inet {
            address 192.168.60.5/24 {
                arp 192.168.60.4 mac 08:00:27:11:22:02;
            }
        }
    }
}

```



Now we are are ready to start to create our tests:


```python
def test_one_packet(trex):
    tx_port, rx_port = trex.get_all_ports()
    trex.reset(ports=[tx_port, rx_port])
    # activate service mode on RX code
    trex.set_service_mode(ports=rx_port)
    # generate a simple UDP packet
    pkt = Ether() / IP() / UDP()
    pkt[IP].src = "192.168.50.4"
    pkt[IP].dst = "192.168.60.4"
    # start a capture
    capture = trex.start_capture(rx_ports=rx_port)
    # push the UDP packet to TX port... we need 'force' because this is under service mode
    print('\nSending 1 UDP packet(s) on port {}'.format(tx_port))
    trex.push_packets(ports=tx_port, pkts=pkt, force=True)
    trex.wait_on_traffic(ports=tx_port, rx_delay_ms=1000)
    # we need to block with Virtualbox because the delay is huge
    time.sleep(0.5)
    rx_pkts = []
    trex.stop_capture(capture_id=capture['id'], output=rx_pkts)
    print('\nRecived {} packets on port {}:\n'.format(len(rx_pkts), rx_port))
    trex.set_service_mode(ports=rx_port, enabled=False)

    # got back one packet
    assert(len(rx_pkts) == 1)
    rx_scapy_pkt = Ether(rx_pkts[0]['binary'])
    # Check if it's the same packet
    assert('UDP' in rx_scapy_pkt)
```

and run them:

```bash
aojea  (e) venv   master  ~  projects  pytest-trex  tests  pytest --config=config.local.yaml
==================================================== test session starts =====================================================
platform linux2 -- Python 2.7.12, pytest-3.2.3, py-1.4.34, pluggy-0.4.0
rootdir: /home/aojea/projects/pytest-trex/tests, inifile: pytest.ini
collected 1 item                                                                                                              

test_simple.py .

================================================== 1 passed in 0.74 seconds ==================================================
 aojea  (e) venv   master  ~  projects  pytest-trex  tests  

```

### TODO

- [ ] It's turned out that is not straightforward to run it in Mac, you need to install sosome things manually and compile zmq.

```sh
brew install --with-python libdnet
pip install pcapy
pip install scapy
```

- [ ] Automate DUT configuration
- [x] Parametrize tests to run with multiple protocols
- [ ] [Run tests against multiple
  devices](https://holgerkrekel.net/2013/11/12/running-tests-against-multiple-devicesresources-in-parallel/)

