#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from src.core.network_monitor import NetworkMonitor
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet
from datetime import datetime, timedelta

@pytest.fixture
def network_monitor():
    """Test için NetworkMonitor örneği oluşturur."""
    return NetworkMonitor()

def create_test_packet(src_ip: str, dst_ip: str, 
                      src_port: int = 12345, dst_port: int = 80,
                      proto: str = 'TCP') -> Packet:
    """Test için paket oluşturur."""
    if proto == 'TCP':
        return IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port)
    else:
        return IP(src=src_ip, dst=dst_ip)/UDP(sport=src_port, dport=dst_port)

def test_analyze_packet(network_monitor):
    """Paket analiz fonksiyonunu test eder."""
    test_packet = create_test_packet('192.168.1.100', '192.168.1.1')
    packet_info = network_monitor.analyze_packet(test_packet)
    
    assert packet_info['src_ip'] == '192.168.1.100'
    assert packet_info['dst_ip'] == '192.168.1.1'
    assert 'timestamp' in packet_info
    assert 'length' in packet_info
    assert 'protocol' in packet_info

def test_detect_port_scan(network_monitor):
    """Port tarama tespitini test eder."""
    src_ip = '192.168.1.100'
    dst_ip = '192.168.1.1'
    
    # 150 farklı porta bağlantı dene (threshold = 100)
    for port in range(1, 151):
        packet = create_test_packet(src_ip, dst_ip, dst_port=port)
        network_monitor.packet_queue.put(packet)
    
    suspicious_scans = network_monitor.detect_port_scan()
    assert len(suspicious_scans) > 0
    assert suspicious_scans[0]['ip'] == src_ip
    assert suspicious_scans[0]['ports_tried'] > 100

def test_detect_ddos_attack(network_monitor):
    """DDoS saldırı tespitini test eder."""
    src_ips = [f'192.168.1.{i}' for i in range(100, 200)]
    target_ip = '192.168.1.1'
    
    # 1100 paket gönder (threshold = 1000)
    for _ in range(1100):
        for src_ip in src_ips[:11]:  # Her IP'den 100 paket
            packet = create_test_packet(src_ip, target_ip)
            network_monitor.packet_queue.put(packet)
    
    suspicious_ddos = network_monitor.detect_ddos_attack()
    assert len(suspicious_ddos) > 0
    assert suspicious_ddos[0]['target_ip'] == target_ip
    assert suspicious_ddos[0]['packet_count'] > 1000

def test_start_stop_capture(network_monitor):
    """Paket yakalama başlatma ve durdurma fonksiyonlarını test eder."""
    network_monitor.start_capture()
    assert network_monitor.is_capturing == True
    assert network_monitor.capture_thread is not None
    
    network_monitor.stop_capture()
    assert network_monitor.is_capturing == False 