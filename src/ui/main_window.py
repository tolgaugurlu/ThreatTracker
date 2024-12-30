#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QStatusBar,
    QTableWidget, QTableWidgetItem, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QColor
from typing import Dict, List
import os
import psutil
from datetime import datetime
from .settings_widget import AyarlarWidget
from .threat_analysis_window import TehditAnalizPenceresi
from src.core.network_scanner import NetworkScanner
import netifaces

class AnaEkran(QMainWindow):
    """ThreatTracker ana pencere sınıfı."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThreatTracker - Advanced Network Security Tool")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0a0a0a;
                color: #33ff33;
            }
            QLabel {
                color: #33ff33;
                font-family: 'Courier New';
            }
            QTableWidget {
                background-color: #1a1a1a;
                color: #33ff33;
                gridline-color: #1f5c1f;
                border: 1px solid #1f5c1f;
                selection-background-color: #2d862d;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #2d862d;
            }
            QHeaderView::section {
                background-color: #1f5c1f;
                color: #33ff33;
                border: 1px solid #1f5c1f;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #1f5c1f;
                background-color: #1a1a1a;
                text-align: center;
                color: #33ff33;
            }
            QProgressBar::chunk {
                background-color: #2d862d;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #33ff33;
                border: 1px solid #1f5c1f;
                padding: 8px 16px;
                border-radius: 3px;
                font-family: 'Courier New';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d862d;
                border: 1px solid #33ff33;
            }
            QPushButton:pressed {
                background-color: #1f5c1f;
            }
            QTabWidget::pane {
                border: 1px solid #1f5c1f;
                background-color: #0a0a0a;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #33ff33;
                border: 1px solid #1f5c1f;
                padding: 8px 16px;
                margin-right: 2px;
                font-family: 'Courier New';
            }
            QTabBar::tab:selected {
                background-color: #2d862d;
                border: 1px solid #33ff33;
            }
            QTabBar::tab:hover {
                background-color: #1f5c1f;
            }
            QGroupBox {
                border: 1px solid #1f5c1f;
                border-radius: 3px;
                margin-top: 1em;
                padding-top: 1em;
                color: #33ff33;
                font-family: 'Courier New';
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #33ff33;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #33ff33;
                border-top: 1px solid #1f5c1f;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1a1a1a;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #2d862d;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QLineEdit {
                background-color: #1a1a1a;
                color: #33ff33;
                border: 1px solid #1f5c1f;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #33ff33;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #33ff33;
                border: 1px solid #1f5c1f;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        # Ana widget ve layout
        self.merkez_widget = QWidget()
        self.setCentralWidget(self.merkez_widget)
        self.ana_layout = QVBoxLayout(self.merkez_widget)
        
        # Durum çubuğu
        self.durum_cubugu = QStatusBar()
        self.setStatusBar(self.durum_cubugu)
        
        # GUI bileşenlerini oluştur
        self._gui_olustur()
        
        # Zamanlayıcıları başlat
        self._zamanlayicilari_baslat()
        
        # İlk güncellemeyi yap
        self._sistem_durumunu_guncelle()
        self.durum_cubugu.showMessage("ThreatTracker initialized | Developed by Tolga Uğurlu | v1.0.0")
        
        # Ağ tarayıcısını başlat
        self.ag_tarayici = NetworkScanner()
        
        # Zamanlayıcıyı başlat
        self.tarama_zamanlayici = QTimer()
        self.tarama_zamanlayici.timeout.connect(self._tarama_sonuclarini_kontrol_et)
        self.tarama_zamanlayici.start(1000)  # Her saniye kontrol et
    
    def _gui_olustur(self):
        """GUI bileşenlerini oluşturur."""
        # Üst bilgi paneli
        self._ust_panel_olustur()
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.ana_layout.addWidget(self.tab_widget)
        
        # Sekmeleri oluştur
        self._gosterge_paneli_olustur()
        self._tehditler_sekmesi_olustur()
        self._sistem_durumu_sekmesi_olustur()
        self._ayarlar_sekmesi_olustur()
    
    def _ust_panel_olustur(self):
        """Üst bilgi panelini oluşturur."""
        ust_panel = QWidget()
        ust_layout = QHBoxLayout(ust_panel)
        
        # Logo ve başlık
        baslik = QLabel("ThreatTracker")
        baslik.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New';
            color: #00ff00;
        """)
        
        # Geliştirici bilgisi
        gelistirici = QLabel("by Tolga Uğurlu")
        gelistirici.setStyleSheet("""
            font-size: 12px;
            font-family: 'Courier New';
            color: #00aa00;
        """)
        
        baslik_layout = QVBoxLayout()
        baslik_layout.addWidget(baslik)
        baslik_layout.addWidget(gelistirici)
        
        ust_layout.addLayout(baslik_layout)
        
        # Durum göstergeleri
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximumWidth(150)
        self.ram_progress = QProgressBar()
        self.ram_progress.setMaximumWidth(150)
        
        cpu_label = QLabel("[CPU]")
        ram_label = QLabel("[RAM]")
        
        ust_layout.addStretch()
        ust_layout.addWidget(cpu_label)
        ust_layout.addWidget(self.cpu_progress)
        ust_layout.addWidget(ram_label)
        ust_layout.addWidget(self.ram_progress)
        
        self.ana_layout.addWidget(ust_panel)
    
    def _gosterge_paneli_olustur(self):
        """Gösterge paneli sekmesini oluşturur."""
        gosterge_widget = QWidget()
        gosterge_layout = QVBoxLayout(gosterge_widget)
        
        # Ağ tarama kontrolleri
        tarama_grup = QGroupBox("[Network Scanning Controls]")
        tarama_layout = QHBoxLayout()
        
        self.tarama_baslat = QPushButton("Start Scan")
        self.tarama_baslat.clicked.connect(self._ag_taramasi_baslat)
        
        self.deauth_baslat = QPushButton("Start Deauth")
        self.deauth_baslat.clicked.connect(self._deauth_saldirisi_baslat)
        
        self.paket_yakala = QPushButton("Capture Packets")
        self.paket_yakala.clicked.connect(self._paket_yakalama_baslat)
        
        for buton in [self.tarama_baslat, self.deauth_baslat, self.paket_yakala]:
            tarama_layout.addWidget(buton)
        
        tarama_grup.setLayout(tarama_layout)
        gosterge_layout.addWidget(tarama_grup)
        
        # Özet bilgiler
        ozet_widget = QWidget()
        ozet_layout = QHBoxLayout(ozet_widget)
        
        # Tehdit sayacı
        self.tehdit_sayaci = QLabel("0")
        self.tehdit_sayaci.setStyleSheet("""
            font-size: 36px;
            color: #ff0000;
            background: #2a2a2a;
            padding: 20px;
            border: 1px solid #ff0000;
            border-radius: 10px;
        """)
        
        ozet_layout.addWidget(QLabel("[Active Threats]"))
        ozet_layout.addWidget(self.tehdit_sayaci)
        ozet_layout.addStretch()
        
        gosterge_layout.addWidget(ozet_widget)
        
        # Son olaylar tablosu
        self.son_olaylar_tablo = QTableWidget()
        self.son_olaylar_tablo.setColumnCount(4)
        self.son_olaylar_tablo.setHorizontalHeaderLabels([
            "Timestamp", "Type", "Source", "Message"
        ])
        self.son_olaylar_tablo.horizontalHeader().setStretchLastSection(True)
        
        gosterge_layout.addWidget(QLabel("[Recent Events]"))
        gosterge_layout.addWidget(self.son_olaylar_tablo)
        
        self.tab_widget.addTab(gosterge_widget, "Dashboard")
    
    def _tehditler_sekmesi_olustur(self):
        """Tehditler sekmesini oluşturur."""
        tehditler_widget = QWidget()
        tehditler_layout = QVBoxLayout(tehditler_widget)
        
        # Tehdit listesi
        self.tehdit_tablosu = QTableWidget()
        self.tehdit_tablosu.setColumnCount(5)
        self.tehdit_tablosu.setHorizontalHeaderLabels([
            "Tespit Zamanı", "Tehdit", "Seviye", "Kaynak", "Durum"
        ])
        self.tehdit_tablosu.horizontalHeader().setStretchLastSection(True)
        self.tehdit_tablosu.itemDoubleClicked.connect(self._tehdit_detaylarini_goster)
        
        tehditler_layout.addWidget(self.tehdit_tablosu)
        
        self.tab_widget.addTab(tehditler_widget, "Tehditler")
    
    def _tehdit_detaylarini_goster(self, item):
        """Seçilen tehdidin detaylarını gösterir.
        
        Args:
            item: Tıklanan tablo öğesi
        """
        row = item.row()
        tehdit_bilgisi = {
            'baslik': self.tehdit_tablosu.item(row, 1).text(),
            'seviye': self.tehdit_tablosu.item(row, 2).text(),
            'kaynak': self.tehdit_tablosu.item(row, 3).text(),
            'durum': self.tehdit_tablosu.item(row, 4).text(),
            'tespit_zamani': datetime.strptime(
                self.tehdit_tablosu.item(row, 0).text(),
                '%d.%m.%Y %H:%M:%S'
            ),
            'ilgili_olaylar': [
                {
                    'zaman': '12.01.2024 15:30:45',
                    'tur': 'Port Tarama',
                    'aciklama': 'Şüpheli port tarama aktivitesi tespit edildi'
                },
                {
                    'zaman': '12.01.2024 15:31:00',
                    'tur': 'Bağlantı Girişimi',
                    'aciklama': 'Yüksek riskli porta bağlantı denemesi'
                }
            ],
            'oneriler': [
                'Şüpheli IP adresini güvenlik duvarında engelleyin',
                'Sistem loglarını detaylı inceleyerek benzer aktiviteleri kontrol edin',
                'İlgili portları geçici olarak kapatmayı değerlendirin',
                'Güvenlik yazılımlarını güncelleyin'
            ]
        }
        
        analiz_penceresi = TehditAnalizPenceresi(tehdit_bilgisi)
        analiz_penceresi.show()
    
    def _sistem_durumu_sekmesi_olustur(self):
        """Sistem durumu sekmesini oluşturur."""
        sistem_widget = QWidget()
        sistem_layout = QVBoxLayout(sistem_widget)
        
        # Sistem metrikleri
        metrikler_widget = QWidget()
        metrikler_layout = QHBoxLayout(metrikler_widget)
        
        self.cpu_label = QLabel("CPU: %0")
        self.ram_label = QLabel("RAM: %0")
        self.disk_label = QLabel("Disk: %0")
        self.baglanti_label = QLabel("Bağlantı: 0")
        
        for label in [self.cpu_label, self.ram_label, 
                     self.disk_label, self.baglanti_label]:
            label.setStyleSheet("""
                font-size: 18px;
                padding: 10px;
                background: #f5f5f5;
                border-radius: 5px;
            """)
            metrikler_layout.addWidget(label)
        
        sistem_layout.addWidget(metrikler_widget)
        
        # Süreç listesi
        self.surec_tablosu = QTableWidget()
        self.surec_tablosu.setColumnCount(5)
        self.surec_tablosu.setHorizontalHeaderLabels([
            "PID", "İsim", "CPU %", "RAM %", "Durum"
        ])
        self.surec_tablosu.horizontalHeader().setStretchLastSection(True)
        
        sistem_layout.addWidget(QLabel("Aktif Süreçler:"))
        sistem_layout.addWidget(self.surec_tablosu)
        
        self.tab_widget.addTab(sistem_widget, "Sistem Durumu")
    
    def _ayarlar_sekmesi_olustur(self):
        """Ayarlar sekmesini oluşturur."""
        ayarlar_widget = AyarlarWidget()
        ayarlar_widget.ayarlar_degisti.connect(self._ayarlar_degisti)
        self.tab_widget.addTab(ayarlar_widget, "Ayarlar")
    
    def _ayarlar_degisti(self, yeni_ayarlar: dict):
        """Ayarlar değiştiğinde çağrılır.
        
        Args:
            yeni_ayarlar: Yeni ayarlar sözlüğü
        """
        # Bildirim aralıklarını güncelle
        self.tehdit_zamanlayici.setInterval(
            yeni_ayarlar['bildirim_araligi']['normal_tehditler'] * 1000
        )
        
        # Sistem durumu güncelleme aralığını güncelle
        self.sistem_zamanlayici.setInterval(
            yeni_ayarlar['bildirim_araligi']['sistem_durumlari'] * 1000
        )
        
        # TODO: Diğer ayarları uygula (bildirim sistemi, veritabanı temizleme, vs.)
        logger.info("Ayarlar uygulandı")
    
    def _zamanlayicilari_baslat(self):
        """Güncelleme zamanlayıcılarını başlatır."""
        # Sistem durumu güncellemesi (her 2 saniyede)
        self.sistem_zamanlayici = QTimer()
        self.sistem_zamanlayici.timeout.connect(self._sistem_durumunu_guncelle)
        self.sistem_zamanlayici.start(2000)
        
        # Tehdit listesi güncellemesi (her 5 saniyede)
        self.tehdit_zamanlayici = QTimer()
        self.tehdit_zamanlayici.timeout.connect(self._tehditleri_guncelle)
        self.tehdit_zamanlayici.start(5000)
    
    def _sistem_durumunu_guncelle(self):
        """Sistem durumu metriklerini günceller."""
        # CPU ve RAM kullanımı
        cpu_yuzde = psutil.cpu_percent()
        ram_yuzde = psutil.virtual_memory().percent
        
        self.cpu_progress.setValue(int(cpu_yuzde))
        self.ram_progress.setValue(int(ram_yuzde))
        
        self.cpu_label.setText(f"CPU: %{cpu_yuzde:.1f}")
        self.ram_label.setText(f"RAM: %{ram_yuzde:.1f}")
        
        # Disk kullanımı
        disk = psutil.disk_usage('/')
        disk_yuzde = disk.percent
        self.disk_label.setText(f"Disk: %{disk_yuzde:.1f}")
        
        # Ağ bağlantıları
        try:
            baglanti_sayisi = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.Error):
            baglanti_sayisi = 0
        self.baglanti_label.setText(f"Bağlantı: {baglanti_sayisi}")
        
        # Süreç listesini güncelle
        self._surecleri_guncelle()
    
    def _surecleri_guncelle(self):
        """Süreç listesini günceller."""
        self.surec_tablosu.setRowCount(0)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                       'memory_percent', 'status']):
            try:
                bilgi = proc.info
                row = self.surec_tablosu.rowCount()
                self.surec_tablosu.insertRow(row)
                
                self.surec_tablosu.setItem(row, 0, QTableWidgetItem(str(bilgi['pid'])))
                self.surec_tablosu.setItem(row, 1, QTableWidgetItem(str(bilgi['name'])))
                
                cpu_percent = bilgi['cpu_percent']
                self.surec_tablosu.setItem(row, 2, QTableWidgetItem(
                    f"{cpu_percent:.1f}" if cpu_percent is not None else "0.0"
                ))
                
                memory_percent = bilgi['memory_percent']
                self.surec_tablosu.setItem(row, 3, QTableWidgetItem(
                    f"{memory_percent:.1f}" if memory_percent is not None else "0.0"
                ))
                
                self.surec_tablosu.setItem(row, 4, QTableWidgetItem(str(bilgi['status'])))
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _tehditleri_guncelle(self):
        """Tehdit listesini günceller."""
        # Örnek tehdit verisi
        tehditler = [
            {
                'zaman': '30.12.2023 21:15:00',
                'tehdit': 'Port Tarama Saldırısı',
                'seviye': 'Yüksek',
                'kaynak': '192.168.1.100',
                'durum': 'Aktif'
            },
            {
                'zaman': '30.12.2023 21:14:30',
                'tehdit': 'Şüpheli Dosya Erişimi',
                'seviye': 'Orta',
                'kaynak': 'C:/Windows/System32',
                'durum': 'İnceleniyor'
            },
            {
                'zaman': '30.12.2023 21:13:45',
                'tehdit': 'Yüksek CPU Kullanımı',
                'seviye': 'Düşük',
                'kaynak': 'chrome.exe',
                'durum': 'İzleniyor'
            }
        ]
        
        self.tehdit_tablosu.setRowCount(len(tehditler))
        for i, tehdit in enumerate(tehditler):
            self.tehdit_tablosu.setItem(i, 0, QTableWidgetItem(tehdit['zaman']))
            self.tehdit_tablosu.setItem(i, 1, QTableWidgetItem(tehdit['tehdit']))
            self.tehdit_tablosu.setItem(i, 2, QTableWidgetItem(tehdit['seviye']))
            self.tehdit_tablosu.setItem(i, 3, QTableWidgetItem(tehdit['kaynak']))
            self.tehdit_tablosu.setItem(i, 4, QTableWidgetItem(tehdit['durum']))
            
            # Seviyeye göre renklendirme
            renk = QColor()
            if tehdit['seviye'] == 'Yüksek':
                renk = QColor('#ffebee')  # Açık kırmızı
            elif tehdit['seviye'] == 'Orta':
                renk = QColor('#fff3e0')  # Açık turuncu
            else:
                renk = QColor('#f1f8e9')  # Açık yeşil
            
            for j in range(5):
                self.tehdit_tablosu.item(i, j).setBackground(renk)
        
        # Tehdit sayacını güncelle
        aktif_tehdit_sayisi = sum(1 for t in tehditler if t['durum'] == 'Aktif')
        self.tehdit_sayaci.setText(str(aktif_tehdit_sayisi))
    
    def _ag_taramasi_baslat(self):
        """Ağ taramasını başlatır."""
        try:
            # Varsayılan ağ arayüzünü bul
            varsayilan_ag = netifaces.gateways()['default'][netifaces.AF_INET][1]
            ag_adresleri = netifaces.ifaddresses(varsayilan_ag)
            ip_adresi = ag_adresleri[netifaces.AF_INET][0]['addr']
            
            # IP aralığını belirle (örn: 192.168.1.0/24)
            ip_araligi = '.'.join(ip_adresi.split('.')[:-1]) + '.0/24'
            
            # Taramayı başlat
            self.ag_tarayici.ag_taramasi_baslat(ip_araligi)
            self.durum_cubugu.showMessage(f"Network scanning started on {ip_araligi}...")
            
            # Butonları güncelle
            self.tarama_baslat.setText("Stop Scan")
            self.tarama_baslat.clicked.disconnect()
            self.tarama_baslat.clicked.connect(self._ag_taramasini_durdur)
            
        except Exception as e:
            self.durum_cubugu.showMessage(f"Error starting network scan: {e}")
    
    def _ag_taramasini_durdur(self):
        """Ağ taramasını durdurur."""
        self.ag_tarayici.ag_taramasini_durdur()
        self.durum_cubugu.showMessage("Network scanning stopped.")
        
        # Butonları güncelle
        self.tarama_baslat.setText("Start Scan")
        self.tarama_baslat.clicked.disconnect()
        self.tarama_baslat.clicked.connect(self._ag_taramasi_baslat)
    
    def _tarama_sonuclarini_kontrol_et(self):
        """Tarama sonuçlarını kontrol eder ve arayüzü günceller."""
        try:
            while not self.ag_tarayici.sonuc_kuyrugu.empty():
                sonuc = self.ag_tarayici.sonuc_kuyrugu.get_nowait()
                
                if sonuc['tip'] == 'cihaz_tespit':
                    cihaz = sonuc['veri']
                    self._cihaz_ekle(cihaz)
                elif sonuc['tip'] == 'hata':
                    self.durum_cubugu.showMessage(f"Scan error: {sonuc['veri']}")
        
        except Exception as e:
            self.durum_cubugu.showMessage(f"Error processing scan results: {e}")
    
    def _cihaz_ekle(self, cihaz: dict):
        """Tespit edilen cihazı tabloya ekler.
        
        Args:
            cihaz: Cihaz bilgilerini içeren sözlük
        """
        row = self.son_olaylar_tablo.rowCount()
        self.son_olaylar_tablo.insertRow(row)
        
        self.son_olaylar_tablo.setItem(row, 0, QTableWidgetItem(cihaz['tespit_zamani']))
        self.son_olaylar_tablo.setItem(row, 1, QTableWidgetItem("Device Found"))
        self.son_olaylar_tablo.setItem(row, 2, QTableWidgetItem(cihaz['ip']))
        
        # Açık port bilgilerini ekle
        acik_port_mesaji = []
        for port in cihaz.get('acik_portlar', []):
            acik_port_mesaji.append(
                f"Port {port['port']} ({port['servis']})"
            )
        
        mesaj = f"MAC: {cihaz['mac']}"
        if acik_port_mesaji:
            mesaj += f" | Open Ports: {', '.join(acik_port_mesaji)}"
        
        self.son_olaylar_tablo.setItem(row, 3, QTableWidgetItem(mesaj))
        
        # Satırı yeşil yap
        for j in range(4):
            self.son_olaylar_tablo.item(row, j).setBackground(QColor('#004400'))
    
    def _deauth_saldirisi_baslat(self):
        """Deauth saldırısını başlatır."""
        # TODO: Deauth saldırısı mantığı eklenecek
        self.durum_cubugu.showMessage("Deauth attack initiated...")
    
    def _paket_yakalama_baslat(self):
        """Paket yakalamayı başlatır."""
        # TODO: Paket yakalama mantığı eklenecek
        self.durum_cubugu.showMessage("Packet capture started...") 