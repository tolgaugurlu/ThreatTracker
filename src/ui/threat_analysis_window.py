#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QTextEdit, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
from typing import Dict, List

class TehditAnalizPenceresi(QMainWindow):
    """Tehdit analiz penceresi sınıfı."""
    
    def __init__(self, tehdit_bilgisi: Dict):
        """TehditAnalizPenceresi sınıfının başlatıcısı.
        
        Args:
            tehdit_bilgisi: Tehdit detaylarını içeren sözlük
        """
        super().__init__()
        self.tehdit_bilgisi = tehdit_bilgisi
        self.setWindowTitle("Tehdit Analizi")
        self.setMinimumSize(1000, 700)
        
        # Ana widget ve layout
        self.merkez_widget = QWidget()
        self.setCentralWidget(self.merkez_widget)
        self.ana_layout = QVBoxLayout(self.merkez_widget)
        
        # GUI bileşenlerini oluştur
        self._gui_olustur()
        
        # Tehdit bilgilerini göster
        self._tehdit_bilgilerini_goster()
    
    def _gui_olustur(self):
        """GUI bileşenlerini oluşturur."""
        # Üst bilgi paneli
        self._ust_panel_olustur()
        
        # Ana içerik bölümü
        icerik_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.ana_layout.addWidget(icerik_splitter)
        
        # Sol panel (Tehdit Detayları)
        self._sol_panel_olustur(icerik_splitter)
        
        # Sağ panel (İlgili Olaylar ve Öneriler)
        self._sag_panel_olustur(icerik_splitter)
        
        # Alt panel (Aksiyon Butonları)
        self._alt_panel_olustur()
    
    def _ust_panel_olustur(self):
        """Üst bilgi panelini oluşturur."""
        ust_panel = QWidget()
        ust_layout = QHBoxLayout(ust_panel)
        
        # Tehdit başlığı
        self.tehdit_baslik = QLabel()
        self.tehdit_baslik.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #d32f2f;
        """)
        ust_layout.addWidget(self.tehdit_baslik)
        
        # Tehdit seviyesi
        self.tehdit_seviyesi = QLabel()
        self.tehdit_seviyesi.setStyleSheet("""
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        """)
        ust_layout.addWidget(self.tehdit_seviyesi)
        
        ust_layout.addStretch()
        
        # Tespit zamanı
        self.tespit_zamani = QLabel()
        ust_layout.addWidget(self.tespit_zamani)
        
        self.ana_layout.addWidget(ust_panel)
    
    def _sol_panel_olustur(self, parent: QSplitter):
        """Sol paneli oluşturur."""
        sol_widget = QWidget()
        sol_layout = QVBoxLayout(sol_widget)
        
        # Tehdit detayları grubu
        detay_grup = QGroupBox("Tehdit Detayları")
        detay_layout = QVBoxLayout()
        
        self.detay_tablo = QTableWidget()
        self.detay_tablo.setColumnCount(2)
        self.detay_tablo.setHorizontalHeaderLabels(["Özellik", "Değer"])
        self.detay_tablo.horizontalHeader().setStretchLastSection(True)
        
        detay_layout.addWidget(self.detay_tablo)
        detay_grup.setLayout(detay_layout)
        sol_layout.addWidget(detay_grup)
        
        parent.addWidget(sol_widget)
    
    def _sag_panel_olustur(self, parent: QSplitter):
        """Sağ paneli oluşturur."""
        sag_widget = QWidget()
        sag_layout = QVBoxLayout(sag_widget)
        
        # İlgili olaylar grubu
        olaylar_grup = QGroupBox("İlgili Olaylar")
        olaylar_layout = QVBoxLayout()
        
        self.olaylar_tablo = QTableWidget()
        self.olaylar_tablo.setColumnCount(3)
        self.olaylar_tablo.setHorizontalHeaderLabels(["Zaman", "Tür", "Açıklama"])
        self.olaylar_tablo.horizontalHeader().setStretchLastSection(True)
        
        olaylar_layout.addWidget(self.olaylar_tablo)
        olaylar_grup.setLayout(olaylar_layout)
        sag_layout.addWidget(olaylar_grup)
        
        # Öneriler grubu
        oneriler_grup = QGroupBox("Öneriler ve Alınacak Aksiyonlar")
        oneriler_layout = QVBoxLayout()
        
        self.oneriler_metin = QTextEdit()
        self.oneriler_metin.setReadOnly(True)
        
        oneriler_layout.addWidget(self.oneriler_metin)
        oneriler_grup.setLayout(oneriler_layout)
        sag_layout.addWidget(oneriler_grup)
        
        parent.addWidget(sag_widget)
    
    def _alt_panel_olustur(self):
        """Alt paneli oluşturur."""
        alt_panel = QWidget()
        alt_layout = QHBoxLayout(alt_panel)
        
        # Aksiyon butonları
        self.engelle_buton = QPushButton("Tehdidi Engelle")
        self.engelle_buton.clicked.connect(self._tehdidi_engelle)
        self.engelle_buton.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        
        self.rapor_buton = QPushButton("Rapor Oluştur")
        self.rapor_buton.clicked.connect(self._rapor_olustur)
        
        self.kapat_buton = QPushButton("Kapat")
        self.kapat_buton.clicked.connect(self.close)
        
        alt_layout.addStretch()
        alt_layout.addWidget(self.engelle_buton)
        alt_layout.addWidget(self.rapor_buton)
        alt_layout.addWidget(self.kapat_buton)
        
        self.ana_layout.addWidget(alt_panel)
    
    def _tehdit_bilgilerini_goster(self):
        """Tehdit bilgilerini arayüzde gösterir."""
        # Üst panel bilgileri
        self.tehdit_baslik.setText(self.tehdit_bilgisi.get('baslik', 'Bilinmeyen Tehdit'))
        
        seviye = self.tehdit_bilgisi.get('seviye', 'Düşük')
        self.tehdit_seviyesi.setText(seviye)
        
        # Seviyeye göre renk belirleme
        if seviye == 'Kritik':
            self.tehdit_seviyesi.setStyleSheet("""
                background-color: #d32f2f;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            """)
        elif seviye == 'Yüksek':
            self.tehdit_seviyesi.setStyleSheet("""
                background-color: #f57c00;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            """)
        else:
            self.tehdit_seviyesi.setStyleSheet("""
                background-color: #fdd835;
                color: black;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            """)
        
        # Tespit zamanı
        zaman = self.tehdit_bilgisi.get('tespit_zamani', datetime.now())
        self.tespit_zamani.setText(f"Tespit Zamanı: {zaman.strftime('%d.%m.%Y %H:%M:%S')}")
        
        # Detay tablosu
        self.detay_tablo.setRowCount(0)
        for key, value in self.tehdit_bilgisi.items():
            if key not in ['baslik', 'seviye', 'tespit_zamani']:
                row = self.detay_tablo.rowCount()
                self.detay_tablo.insertRow(row)
                self.detay_tablo.setItem(row, 0, QTableWidgetItem(str(key)))
                self.detay_tablo.setItem(row, 1, QTableWidgetItem(str(value)))
        
        # İlgili olaylar
        olaylar = self.tehdit_bilgisi.get('ilgili_olaylar', [])
        self.olaylar_tablo.setRowCount(len(olaylar))
        for i, olay in enumerate(olaylar):
            self.olaylar_tablo.setItem(i, 0, QTableWidgetItem(olay.get('zaman', '')))
            self.olaylar_tablo.setItem(i, 1, QTableWidgetItem(olay.get('tur', '')))
            self.olaylar_tablo.setItem(i, 2, QTableWidgetItem(olay.get('aciklama', '')))
        
        # Öneriler
        oneriler = self.tehdit_bilgisi.get('oneriler', [])
        self.oneriler_metin.setHtml("<br>".join([
            f"• {oneri}" for oneri in oneriler
        ]))
    
    def _tehdidi_engelle(self):
        """Tehdidi engelleme aksiyonunu gerçekleştirir."""
        # TODO: Tehdit engelleme mantığı eklenecek
        pass
    
    def _rapor_olustur(self):
        """Tehdit raporu oluşturur."""
        # TODO: Rapor oluşturma mantığı eklenecek
        pass 