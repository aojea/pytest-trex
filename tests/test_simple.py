import stl_path
import pytest
import time
from trex_stl_lib.api import *
"""
An example on how to use TRex for functional tests

It can be used for various tasks and can replace simple Pagent/Scapy
low rate tests

TODO include the pyvcluster logic
"""


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
