#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
from datetime import datetime
from loguru import logger
from typing import Dict, List, Optional
import threading
import queue
import netifaces
import netaddr

class NetworkMonitor:
    """Ağ trafiğini izleyen ve analiz eden sınıf."""
    
    def __init__(self):
        """NetworkMonitor sınıfının başlatıcısı."""
        self.packet_queue = queue.Queue()
        self.is_capturing = False
        self.capture_thread = None
        self.known_hosts: Dict[str, Dict] = {}
        self.suspicious_ips: List[str] = []
        logger.info("NetworkMonitor başlatıldı")
    
    def start_capture(self, interface: str = None):
        """Paket yakalamayı başlatır.
        
        Args:
            interface: Dinlenecek ağ arayüzü (None ise varsayılan arayüz kullanılır)
        """
        if self.is_capturing:
            logger.warning("Paket yakalama zaten çalışıyor")
            return
            
        if not interface:
            interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(interface,),
            daemon=True
        )
        self.capture_thread.start()
        logger.info(f"{interface} arayüzünde paket yakalama başlatıldı")
    
    def stop_capture(self):
        """Paket yakalamayı durdurur."""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join()
            logger.info("Paket yakalama durduruldu")
    
    def _capture_packets(self, interface: str):
        """Paketleri yakalar ve kuyruğa ekler.
        
        Args:
            interface: Dinlenecek ağ arayüzü
        """
        def packet_callback(packet):
            if not self.is_capturing:
                return
            if IP in packet:
                self.packet_queue.put(packet)
        
        scapy.sniff(
            iface=interface,
            prn=packet_callback,
            store=False,
            stop_filter=lambda _: not self.is_capturing
        )
    
    def analyze_packet(self, packet) -> Dict:
        """Tek bir paketi analiz eder.
        
        Args:
            packet: Scapy paketi
            
        Returns:
            Dict: Paket bilgilerini içeren sözlük
        """
        packet_info = {
            'timestamp': datetime.now(),
            'src_ip': packet[IP].src,
            'dst_ip': packet[IP].dst,
            'protocol': packet[IP].proto,
            'length': len(packet),
            'ttl': packet[IP].ttl
        }
        
        if TCP in packet:
            packet_info.update({
                'src_port': packet[TCP].sport,
                'dst_port': packet[TCP].dport,
                'tcp_flags': packet[TCP].flags
            })
        elif UDP in packet:
            packet_info.update({
                'src_port': packet[UDP].sport,
                'dst_port': packet[UDP].dport
            })
            
        return packet_info
    
    def detect_port_scan(self, threshold: int = 100) -> List[Dict]:
        """Port tarama aktivitelerini tespit eder.
        
        Args:
            threshold: Şüpheli sayılacak bağlantı denemesi sayısı
            
        Returns:
            List[Dict]: Şüpheli IP'leri ve port tarama bilgilerini içeren liste
        """
        port_scan_attempts = {}
        suspicious_scans = []
        
        while not self.packet_queue.empty():
            packet = self.packet_queue.get()
            if TCP in packet:
                src_ip = packet[IP].src
                if src_ip not in port_scan_attempts:
                    port_scan_attempts[src_ip] = set()
                port_scan_attempts[src_ip].add(packet[TCP].dport)
                
                if len(port_scan_attempts[src_ip]) > threshold:
                    suspicious_scans.append({
                        'ip': src_ip,
                        'ports_tried': len(port_scan_attempts[src_ip]),
                        'timestamp': datetime.now()
                    })
                    if src_ip not in self.suspicious_ips:
                        self.suspicious_ips.append(src_ip)
                        logger.warning(f"Olası port tarama tespit edildi: {src_ip}")
        
        return suspicious_scans
    
    def detect_ddos_attack(self, time_window: int = 60, 
                          packet_threshold: int = 1000) -> List[Dict]:
        """DDoS saldırı belirtilerini tespit eder.
        
        Args:
            time_window: İzlenecek zaman penceresi (saniye)
            packet_threshold: Şüpheli sayılacak paket sayısı
            
        Returns:
            List[Dict]: Şüpheli DDoS aktivitelerini içeren liste
        """
        ddos_attempts = {}
        suspicious_ddos = []
        current_time = datetime.now()
        
        while not self.packet_queue.empty():
            packet = self.packet_queue.get()
            if IP in packet:
                dst_ip = packet[IP].dst
                if dst_ip not in ddos_attempts:
                    ddos_attempts[dst_ip] = []
                
                ddos_attempts[dst_ip].append(current_time)
                
                # Zaman penceresi dışındaki paketleri temizle
                ddos_attempts[dst_ip] = [
                    t for t in ddos_attempts[dst_ip] 
                    if (current_time - t).seconds <= time_window
                ]
                
                if len(ddos_attempts[dst_ip]) > packet_threshold:
                    suspicious_ddos.append({
                        'target_ip': dst_ip,
                        'packet_count': len(ddos_attempts[dst_ip]),
                        'timestamp': current_time
                    })
                    logger.warning(f"Olası DDoS saldırısı tespit edildi: {dst_ip}")
        
        return suspicious_ddos

if __name__ == "__main__":
    # Test kodu
    monitor = NetworkMonitor()
    monitor.start_capture()
    try:
        while True:
            port_scans = monitor.detect_port_scan()
            ddos_attacks = monitor.detect_ddos_attack()
            if port_scans:
                print("Port tarama tespiti:", port_scans)
            if ddos_attacks:
                print("DDoS saldırı tespiti:", ddos_attacks)
    except KeyboardInterrupt:
        monitor.stop_capture()
        print("İzleme durduruldu") 