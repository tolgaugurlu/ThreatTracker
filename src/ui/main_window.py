#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QStatusBar,
    QTableWidget, QTableWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QColor
from typing import Dict, List
import os
import psutil
from datetime import datetime
from .settings_widget import AyarlarWidget
from .threat_analysis_window import TehditAnalizPenceresi

class AnaEkran(QMainWindow):
    """ThreatTracker ana pencere sınıfı."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThreatTracker - Güvenlik İzleme Sistemi")
        self.setMinimumSize(1200, 800)
        
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
        self.durum_cubugu.showMessage("ThreatTracker başlatıldı")
    
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
        baslik.setStyleSheet("font-size: 24px; font-weight: bold;")
        ust_layout.addWidget(baslik)
        
        # Durum göstergeleri
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximumWidth(150)
        self.ram_progress = QProgressBar()
        self.ram_progress.setMaximumWidth(150)
        
        cpu_label = QLabel("CPU:")
        ram_label = QLabel("RAM:")
        
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
        
        # Özet bilgiler
        ozet_widget = QWidget()
        ozet_layout = QHBoxLayout(ozet_widget)
        
        # Tehdit sayacı
        self.tehdit_sayaci = QLabel("0")
        self.tehdit_sayaci.setStyleSheet("""
            font-size: 36px;
            color: red;
            background: #ffebee;
            padding: 20px;
            border-radius: 10px;
        """)
        
        ozet_layout.addWidget(QLabel("Aktif Tehditler:"))
        ozet_layout.addWidget(self.tehdit_sayaci)
        ozet_layout.addStretch()
        
        gosterge_layout.addWidget(ozet_widget)
        
        # Son olaylar tablosu
        self.son_olaylar_tablo = QTableWidget()
        self.son_olaylar_tablo.setColumnCount(4)
        self.son_olaylar_tablo.setHorizontalHeaderLabels([
            "Zaman", "Tip", "Kaynak", "Mesaj"
        ])
        self.son_olaylar_tablo.horizontalHeader().setStretchLastSection(True)
        
        gosterge_layout.addWidget(QLabel("Son Olaylar:"))
        gosterge_layout.addWidget(self.son_olaylar_tablo)
        
        self.tab_widget.addTab(gosterge_widget, "Gösterge Paneli")
    
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
        baglanti_sayisi = len(psutil.net_connections())
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
                self.surec_tablosu.setItem(row, 1, QTableWidgetItem(bilgi['name']))
                self.surec_tablosu.setItem(row, 2, QTableWidgetItem(f"{bilgi['cpu_percent']:.1f}"))
                self.surec_tablosu.setItem(row, 3, QTableWidgetItem(f"{bilgi['memory_percent']:.1f}"))
                self.surec_tablosu.setItem(row, 4, QTableWidgetItem(bilgi['status']))
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _tehditleri_guncelle(self):
        """Tehdit listesini günceller."""
        # TODO: Veritabanından tehditleri çek ve tabloyu güncelle
        pass 