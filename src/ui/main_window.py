#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QStatusBar, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import psutil
import datetime
from loguru import logger

class MainWindow(QMainWindow):
    """Ana pencere sınıfı."""
    
    def __init__(self):
        """MainWindow sınıfının başlatıcısı."""
        super().__init__()
        
        # Pencere ayarları
        self.setWindowTitle("ThreatTracker - Güvenlik İzleme Aracı")
        self.setGeometry(100, 100, 1200, 800)
        
        # Arayüz bileşenlerini oluştur
        self._arayuz_olustur()
        
        # Zamanlayıcıları başlat
        self._zamanlayicilari_baslat()
        
        logger.info("Ana pencere başlatıldı")
    
    def _arayuz_olustur(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Ana widget ve layout
        merkez_widget = QWidget()
        self.setCentralWidget(merkez_widget)
        
        ana_layout = QVBoxLayout()
        merkez_widget.setLayout(ana_layout)
        
        # Sekme widget'ı
        sekmeler = QTabWidget()
        ana_layout.addWidget(sekmeler)
        
        # Gösterge paneli sekmesi
        gosterge_paneli = QWidget()
        sekmeler.addTab(gosterge_paneli, "Gösterge Paneli")
        self._gosterge_paneli_olustur(gosterge_paneli)
        
        # Tehditler sekmesi
        tehditler = QWidget()
        sekmeler.addTab(tehditler, "Tehditler")
        self._tehditler_sekmesi_olustur(tehditler)
        
        # Sistem durumu sekmesi
        sistem_durumu = QWidget()
        sekmeler.addTab(sistem_durumu, "Sistem Durumu")
        self._sistem_durumu_sekmesi_olustur(sistem_durumu)
        
        # Ayarlar sekmesi
        ayarlar = QWidget()
        sekmeler.addTab(ayarlar, "Ayarlar")
        self._ayarlar_sekmesi_olustur(ayarlar)
        
        # Durum çubuğu
        self.durum_cubugu = QStatusBar()
        self.setStatusBar(self.durum_cubugu)
        self.durum_cubugu.showMessage("Hazır")
    
    def _gosterge_paneli_olustur(self, parent):
        """Gösterge paneli sekmesini oluşturur."""
        layout = QVBoxLayout()
        parent.setLayout(layout)
        
        # Başlık
        baslik = QLabel("Sistem Güvenlik Durumu")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(baslik)
        
        # Durum göstergeleri
        gostergeler_layout = QHBoxLayout()
        
        # CPU kullanımı
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_label = QLabel("CPU: 0%")
        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        gostergeler_layout.addLayout(cpu_layout)
        
        # RAM kullanımı
        self.ram_progress = QProgressBar()
        self.ram_progress.setMaximum(100)
        self.ram_label = QLabel("RAM: 0%")
        ram_layout = QVBoxLayout()
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_progress)
        gostergeler_layout.addLayout(ram_layout)
        
        layout.addLayout(gostergeler_layout)
        
        # Aktif bağlantılar tablosu
        self.baglantilar_tablo = QTableWidget()
        self.baglantilar_tablo.setColumnCount(5)
        self.baglantilar_tablo.setHorizontalHeaderLabels([
            "Protokol", "Yerel Adres", "Uzak Adres", "Durum", "PID"
        ])
        layout.addWidget(self.baglantilar_tablo)
    
    def _tehditler_sekmesi_olustur(self, parent):
        """Tehditler sekmesini oluşturur."""
        layout = QVBoxLayout()
        parent.setLayout(layout)
        
        # Tehdit listesi tablosu
        self.tehditler_tablo = QTableWidget()
        self.tehditler_tablo.setColumnCount(5)
        self.tehditler_tablo.setHorizontalHeaderLabels([
            "Zaman", "Tehdit", "Seviye", "Kaynak", "Durum"
        ])
        layout.addWidget(self.tehditler_tablo)
        
        # Kontrol butonları
        butonlar_layout = QHBoxLayout()
        
        self.tara_buton = QPushButton("Güvenlik Taraması Başlat")
        self.tara_buton.clicked.connect(self._guvenlik_taramasi_baslat)
        butonlar_layout.addWidget(self.tara_buton)
        
        self.temizle_buton = QPushButton("Tehditleri Temizle")
        self.temizle_buton.clicked.connect(self._tehditleri_temizle)
        butonlar_layout.addWidget(self.temizle_buton)
        
        layout.addLayout(butonlar_layout)
    
    def _sistem_durumu_sekmesi_olustur(self, parent):
        """Sistem durumu sekmesini oluşturur."""
        layout = QVBoxLayout()
        parent.setLayout(layout)
        
        # Süreçler tablosu
        self.surecler_tablo = QTableWidget()
        self.surecler_tablo.setColumnCount(5)
        self.surecler_tablo.setHorizontalHeaderLabels([
            "PID", "İsim", "CPU %", "RAM %", "Durum"
        ])
        layout.addWidget(self.surecler_tablo)
        
        # Disk kullanımı
        self.disk_label = QLabel("Disk Kullanımı: Hesaplanıyor...")
        layout.addWidget(self.disk_label)
        
        # Ağ kullanımı
        self.ag_label = QLabel("Ağ Kullanımı: Hesaplanıyor...")
        layout.addWidget(self.ag_label)
    
    def _ayarlar_sekmesi_olustur(self, parent):
        """Ayarlar sekmesini oluşturur."""
        layout = QVBoxLayout()
        parent.setLayout(layout)
        
        # Bildirim ayarları
        bildirim_label = QLabel("Bildirim Ayarları")
        bildirim_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(bildirim_label)
        
        self.bildirim_buton = QPushButton("Bildirimleri Yapılandır")
        layout.addWidget(self.bildirim_buton)
        
        # Tarama ayarları
        tarama_label = QLabel("Tarama Ayarları")
        tarama_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(tarama_label)
        
        self.tarama_buton = QPushButton("Tarama Ayarlarını Yapılandır")
        layout.addWidget(self.tarama_buton)
        
        # Boşluk ekle
        layout.addStretch()
    
    def _zamanlayicilari_baslat(self):
        """Güncelleme zamanlayıcılarını başlatır."""
        # Sistem durumu güncelleyici
        self.sistem_zamanlayici = QTimer()
        self.sistem_zamanlayici.timeout.connect(self._sistem_durumunu_guncelle)
        self.sistem_zamanlayici.start(2000)  # 2 saniyede bir
        
        # Süreç listesi güncelleyici
        self.surec_zamanlayici = QTimer()
        self.surec_zamanlayici.timeout.connect(self._surecleri_guncelle)
        self.surec_zamanlayici.start(5000)  # 5 saniyede bir
        
        # Tehdit listesi güncelleyici
        self.tehdit_zamanlayici = QTimer()
        self.tehdit_zamanlayici.timeout.connect(self._tehditleri_guncelle)
        self.tehdit_zamanlayici.start(10000)  # 10 saniyede bir
    
    def _sistem_durumunu_guncelle(self):
        """Sistem durumu göstergelerini günceller."""
        try:
            # CPU ve RAM kullanımı
            cpu_yuzde = psutil.cpu_percent()
            ram_yuzde = psutil.virtual_memory().percent
            
            self.cpu_progress.setValue(int(cpu_yuzde))
            self.cpu_label.setText(f"CPU: %{cpu_yuzde:.1f}")
            
            self.ram_progress.setValue(int(ram_yuzde))
            self.ram_label.setText(f"RAM: %{ram_yuzde:.1f}")
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            self.disk_label.setText(
                f"Disk Kullanımı: %{disk.percent:.1f} "
                f"(Toplam: {disk.total // (2**30)} GB, "
                f"Boş: {disk.free // (2**30)} GB)"
            )
            
            # Ağ kullanımı
            ag = psutil.net_io_counters()
            self.ag_label.setText(
                f"Ağ Kullanımı - Gönderilen: {ag.bytes_sent // (2**20)} MB, "
                f"Alınan: {ag.bytes_recv // (2**20)} MB"
            )
            
            # Aktif bağlantılar
            self.baglantilar_tablo.setRowCount(0)
            for conn in psutil.net_connections():
                row = self.baglantilar_tablo.rowCount()
                self.baglantilar_tablo.insertRow(row)
                
                self.baglantilar_tablo.setItem(
                    row, 0, QTableWidgetItem(conn.type)
                )
                self.baglantilar_tablo.setItem(
                    row, 1, QTableWidgetItem(f"{conn.laddr.ip}:{conn.laddr.port}")
                )
                if conn.raddr:
                    self.baglantilar_tablo.setItem(
                        row, 2, 
                        QTableWidgetItem(f"{conn.raddr.ip}:{conn.raddr.port}")
                    )
                else:
                    self.baglantilar_tablo.setItem(row, 2, QTableWidgetItem("-"))
                self.baglantilar_tablo.setItem(
                    row, 3, QTableWidgetItem(conn.status)
                )
                self.baglantilar_tablo.setItem(
                    row, 4, QTableWidgetItem(str(conn.pid or "-"))
                )
        
        except Exception as e:
            logger.error(f"Sistem durumu güncellenirken hata: {e}")
            self.durum_cubugu.showMessage(
                "Sistem durumu güncellenirken hata oluştu!", 5000
            )
    
    def _surecleri_guncelle(self):
        """Süreç listesini günceller."""
        try:
            self.surecler_tablo.setRowCount(0)
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                          'memory_percent', 'status']):
                try:
                    bilgi = proc.info
                    row = self.surecler_tablo.rowCount()
                    self.surecler_tablo.insertRow(row)
                    
                    self.surecler_tablo.setItem(
                        row, 0, QTableWidgetItem(str(bilgi['pid']))
                    )
                    self.surecler_tablo.setItem(
                        row, 1, QTableWidgetItem(bilgi['name'])
                    )
                    self.surecler_tablo.setItem(
                        row, 2, QTableWidgetItem(f"{bilgi['cpu_percent']:.1f}")
                    )
                    self.surecler_tablo.setItem(
                        row, 3, QTableWidgetItem(f"{bilgi['memory_percent']:.1f}")
                    )
                    self.surecler_tablo.setItem(
                        row, 4, QTableWidgetItem(bilgi['status'])
                    )
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Süreç listesi güncellenirken hata: {e}")
            self.durum_cubugu.showMessage(
                "Süreç listesi güncellenirken hata oluştu!", 5000
            )
    
    def _tehditleri_guncelle(self):
        """Tehdit listesini günceller."""
        try:
            # Örnek tehdit verileri (gerçek uygulamada bu veriler
            # anomali tespiti ve güvenlik taraması sonuçlarından gelecek)
            tehditler = [
                {
                    'zaman': datetime.datetime.now().strftime('%H:%M:%S'),
                    'tehdit': 'Port Tarama Girişimi',
                    'seviye': 'Yüksek',
                    'kaynak': '192.168.1.100',
                    'durum': 'Aktif'
                },
                {
                    'zaman': datetime.datetime.now().strftime('%H:%M:%S'),
                    'tehdit': 'Şüpheli Bağlantı',
                    'seviye': 'Orta',
                    'kaynak': '10.0.0.50',
                    'durum': 'İnceleniyor'
                }
            ]
            
            self.tehditler_tablo.setRowCount(0)
            for tehdit in tehditler:
                row = self.tehditler_tablo.rowCount()
                self.tehditler_tablo.insertRow(row)
                
                self.tehditler_tablo.setItem(
                    row, 0, QTableWidgetItem(tehdit['zaman'])
                )
                self.tehditler_tablo.setItem(
                    row, 1, QTableWidgetItem(tehdit['tehdit'])
                )
                self.tehditler_tablo.setItem(
                    row, 2, QTableWidgetItem(tehdit['seviye'])
                )
                self.tehditler_tablo.setItem(
                    row, 3, QTableWidgetItem(tehdit['kaynak'])
                )
                self.tehditler_tablo.setItem(
                    row, 4, QTableWidgetItem(tehdit['durum'])
                )
        
        except Exception as e:
            logger.error(f"Tehdit listesi güncellenirken hata: {e}")
            self.durum_cubugu.showMessage(
                "Tehdit listesi güncellenirken hata oluştu!", 5000
            )
    
    def _guvenlik_taramasi_baslat(self):
        """Güvenlik taraması başlatır."""
        self.durum_cubugu.showMessage("Güvenlik taraması başlatılıyor...")
        self.tara_buton.setEnabled(False)
        # TODO: Güvenlik taraması işlemleri
        
    def _tehditleri_temizle(self):
        """Tehdit listesini temizler."""
        self.tehditler_tablo.setRowCount(0)
        self.durum_cubugu.showMessage("Tehdit listesi temizlendi")
    
    def closeEvent(self, event):
        """Pencere kapatılırken çağrılır."""
        # Zamanlayıcıları durdur
        self.sistem_zamanlayici.stop()
        self.surec_zamanlayici.stop()
        self.tehdit_zamanlayici.stop()
        
        logger.info("Ana pencere kapatıldı")
        event.accept() 