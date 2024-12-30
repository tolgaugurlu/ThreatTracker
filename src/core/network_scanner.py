#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scapy.all import ARP, Ether, srp, IP, TCP, sr1, RandShort
from typing import List, Dict
import threading
import queue
import time
from datetime import datetime
import netifaces

class NetworkScanner:
    """Ağ tarama ve saldırı sınıfı."""
    
    def __init__(self):
        """NetworkScanner sınıfının başlatıcısı."""
        self.sonuc_kuyrugu = queue.Queue()
        self.tarama_aktif = False
        self.paket_yakalama_aktif = False
    
    def ag_taramasi_baslat(self, ip_araligi: str):
        """Ağ taramasını başlatır.
        
        Args:
            ip_araligi: Taranacak IP aralığı (örn: 192.168.1.0/24)
        """
        self.tarama_aktif = True
        threading.Thread(
            target=self._ag_tara,
            args=(ip_araligi,),
            daemon=True
        ).start()
    
    def ag_taramasini_durdur(self):
        """Ağ taramasını durdurur."""
        self.tarama_aktif = False
    
    def _ag_tara(self, ip_araligi: str):
        """Ağdaki cihazları tarar.
        
        Args:
            ip_araligi: Taranacak IP aralığı
        """
        try:
            # ARP taraması yap
            arp = ARP(pdst=ip_araligi)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            paket = ether/arp
            
            sonuc = srp(paket, timeout=3, verbose=0)[0]
            
            for gonderilen, alinan in sonuc:
                if not self.tarama_aktif:
                    break
                    
                cihaz = {
                    'ip': alinan.psrc,
                    'mac': alinan.hwsrc,
                    'tespit_zamani': datetime.now().strftime('%H:%M:%S'),
                    'durum': 'Aktif'
                }
                
                # Port taraması yap
                acik_portlar = self._port_tara(cihaz['ip'])
                cihaz['acik_portlar'] = acik_portlar
                
                self.sonuc_kuyrugu.put({
                    'tip': 'cihaz_tespit',
                    'veri': cihaz
                })
        
        except Exception as e:
            self.sonuc_kuyrugu.put({
                'tip': 'hata',
                'veri': str(e)
            })
    
    def _port_tara(self, hedef_ip: str, port_listesi: List[int] = None) -> List[Dict]:
        """Belirtilen IP'deki portları tarar.
        
        Args:
            hedef_ip: Hedef IP adresi
            port_listesi: Taranacak port listesi (None ise yaygın portlar taranır)
            
        Returns:
            List[Dict]: Açık portların listesi
        """
        if port_listesi is None:
            port_listesi = [20, 21, 22, 23, 25, 53, 80, 110, 
                          111, 135, 139, 143, 443, 445, 993, 
                          995, 1723, 3306, 3389, 5900, 8080]
        
        acik_portlar = []
        
        for port in port_listesi:
            if not self.tarama_aktif:
                break
                
            try:
                # SYN taraması
                syn_paket = IP(dst=hedef_ip)/TCP(
                    sport=RandShort(),
                    dport=port,
                    flags="S"
                )
                
                yanit = sr1(syn_paket, timeout=1, verbose=0)
                
                if yanit is not None:
                    if yanit.haslayer(TCP):
                        if yanit[TCP].flags == 0x12:  # SYN-ACK
                            # RST paketi gönder
                            rst_paket = IP(dst=hedef_ip)/TCP(
                                sport=syn_paket[TCP].sport,
                                dport=port,
                                flags="R"
                            )
                            sr1(rst_paket, timeout=1, verbose=0)
                            
                            acik_portlar.append({
                                'port': port,
                                'durum': 'Açık',
                                'servis': self._servis_tahmin_et(port)
                            })
            
            except Exception:
                continue
        
        return acik_portlar
    
    def _servis_tahmin_et(self, port: int) -> str:
        """Port numarasına göre muhtemel servisi tahmin eder.
        
        Args:
            port: Port numarası
            
        Returns:
            str: Tahmini servis adı
        """
        servisler = {
            20: 'FTP-Data',
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            111: 'RPC',
            135: 'RPC',
            139: 'NetBIOS',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            993: 'IMAP-SSL',
            995: 'POP3-SSL',
            1723: 'PPTP',
            3306: 'MySQL',
            3389: 'RDP',
            5900: 'VNC',
            8080: 'HTTP-Proxy'
        }
        return servisler.get(port, 'Bilinmiyor')
    
    def deauth_saldirisi_baslat(self, hedef_mac: str, ag_mac: str):
        """Deauth saldırısını başlatır.
        
        Args:
            hedef_mac: Hedef cihazın MAC adresi
            ag_mac: Ağ cihazının MAC adresi
        """
        # TODO: Deauth saldırısı mantığı eklenecek
        # Not: Bu özellik etik ve yasal sınırlar içinde kullanılmalıdır
        pass
    
    def paket_yakalama_baslat(self):
        """Paket yakalamayı başlatır."""
        self.paket_yakalama_aktif = True
        threading.Thread(
            target=self._paket_yakala,
            daemon=True
        ).start()
    
    def paket_yakalamayi_durdur(self):
        """Paket yakalamayı durdurur."""
        self.paket_yakalama_aktif = False
    
    def _paket_yakala(self):
        """Ağ paketlerini yakalar."""
        # TODO: Paket yakalama mantığı eklenecek
        pass 