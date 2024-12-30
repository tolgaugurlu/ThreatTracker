#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QGroupBox, QTabWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import json
import os
from loguru import logger

class AyarlarWidget(QWidget):
    """Ayarlar sekmesi widget'ı."""
    
    # Ayarlar değiştiğinde sinyal gönder
    ayarlar_degisti = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ayarlar = self._varsayilan_ayarlari_yukle()
        self._gui_olustur()
        self._ayarlari_guncelle()
    
    def _varsayilan_ayarlari_yukle(self) -> dict:
        """Varsayılan ayarları yükler."""
        varsayilan_ayarlar = {
            'email': {
                'aktif': False,
                'smtp_sunucu': 'smtp.gmail.com',
                'smtp_port': 587,
                'gonderen_email': '',
                'gonderen_sifre': '',
                'alici_email': ''
            },
            'masaustu_bildirimleri': {
                'aktif': True,
                'kritik_tehditler': True,
                'sistem_durumlari': True
            },
            'bildirim_araligi': {
                'kritik_tehditler': 300,  # 5 dakika
                'normal_tehditler': 1800,  # 30 dakika
                'sistem_durumlari': 3600   # 1 saat
            },
            'sistem': {
                'otomatik_baslat': True,
                'arkaplanda_calis': True,
                'log_tutma_suresi': 30,  # gün
                'veri_temizleme_suresi': 90  # gün
            }
        }
        
        # Ayarlar dosyasını kontrol et
        ayarlar_dizini = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
        ayarlar_dosyasi = os.path.join(ayarlar_dizini, 'settings.json')
        
        if os.path.exists(ayarlar_dosyasi):
            try:
                with open(ayarlar_dosyasi, 'r', encoding='utf-8') as f:
                    kayitli_ayarlar = json.load(f)
                varsayilan_ayarlar.update(kayitli_ayarlar)
            except Exception as e:
                logger.error(f"Ayarlar dosyası yüklenirken hata: {e}")
        
        return varsayilan_ayarlar
    
    def _gui_olustur(self):
        """GUI bileşenlerini oluşturur."""
        ana_layout = QVBoxLayout(self)
        
        # Ayarlar sekmelerini oluştur
        self.tab_widget = QTabWidget()
        ana_layout.addWidget(self.tab_widget)
        
        # Bildirim ayarları sekmesi
        self._bildirim_ayarlari_sekmesi_olustur()
        
        # Sistem ayarları sekmesi
        self._sistem_ayarlari_sekmesi_olustur()
        
        # Kaydet ve İptal butonları
        butonlar_layout = QHBoxLayout()
        
        self.kaydet_buton = QPushButton("Kaydet")
        self.kaydet_buton.clicked.connect(self._ayarlari_kaydet)
        
        self.iptal_buton = QPushButton("İptal")
        self.iptal_buton.clicked.connect(self._ayarlari_guncelle)
        self.iptal_buton.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        butonlar_layout.addStretch()
        butonlar_layout.addWidget(self.iptal_buton)
        butonlar_layout.addWidget(self.kaydet_buton)
        
        ana_layout.addLayout(butonlar_layout)
    
    def _bildirim_ayarlari_sekmesi_olustur(self):
        """Bildirim ayarları sekmesini oluşturur."""
        bildirim_widget = QWidget()
        bildirim_layout = QVBoxLayout(bildirim_widget)
        
        # Email ayarları grubu
        email_grup = QGroupBox("Email Bildirimleri")
        email_layout = QFormLayout()
        
        self.email_aktif = QCheckBox("Email bildirimlerini aktifleştir")
        email_layout.addRow(self.email_aktif)
        
        self.smtp_sunucu = QLineEdit()
        email_layout.addRow("SMTP Sunucu:", self.smtp_sunucu)
        
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        email_layout.addRow("SMTP Port:", self.smtp_port)
        
        self.gonderen_email = QLineEdit()
        email_layout.addRow("Gönderen Email:", self.gonderen_email)
        
        self.gonderen_sifre = QLineEdit()
        self.gonderen_sifre.setEchoMode(QLineEdit.EchoMode.Password)
        email_layout.addRow("Gönderen Şifre:", self.gonderen_sifre)
        
        self.alici_email = QLineEdit()
        email_layout.addRow("Alıcı Email:", self.alici_email)
        
        email_grup.setLayout(email_layout)
        bildirim_layout.addWidget(email_grup)
        
        # Masaüstü bildirimleri grubu
        masaustu_grup = QGroupBox("Masaüstü Bildirimleri")
        masaustu_layout = QVBoxLayout()
        
        self.masaustu_aktif = QCheckBox("Masaüstü bildirimlerini aktifleştir")
        self.kritik_tehditler = QCheckBox("Kritik tehditlerde bildir")
        self.sistem_durumlari = QCheckBox("Sistem durumlarında bildir")
        
        masaustu_layout.addWidget(self.masaustu_aktif)
        masaustu_layout.addWidget(self.kritik_tehditler)
        masaustu_layout.addWidget(self.sistem_durumlari)
        
        masaustu_grup.setLayout(masaustu_layout)
        bildirim_layout.addWidget(masaustu_grup)
        
        # Bildirim aralıkları grubu
        aralik_grup = QGroupBox("Bildirim Aralıkları (saniye)")
        aralik_layout = QFormLayout()
        
        self.kritik_aralik = QSpinBox()
        self.kritik_aralik.setRange(60, 3600)
        aralik_layout.addRow("Kritik Tehditler:", self.kritik_aralik)
        
        self.normal_aralik = QSpinBox()
        self.normal_aralik.setRange(300, 7200)
        aralik_layout.addRow("Normal Tehditler:", self.normal_aralik)
        
        self.sistem_aralik = QSpinBox()
        self.sistem_aralik.setRange(600, 14400)
        aralik_layout.addRow("Sistem Durumları:", self.sistem_aralik)
        
        aralik_grup.setLayout(aralik_layout)
        bildirim_layout.addWidget(aralik_grup)
        
        self.tab_widget.addTab(bildirim_widget, "Bildirimler")
    
    def _sistem_ayarlari_sekmesi_olustur(self):
        """Sistem ayarları sekmesini oluşturur."""
        sistem_widget = QWidget()
        sistem_layout = QVBoxLayout(sistem_widget)
        
        # Genel ayarlar grubu
        genel_grup = QGroupBox("Genel Ayarlar")
        genel_layout = QVBoxLayout()
        
        self.otomatik_baslat = QCheckBox("Sistem başlangıcında otomatik başlat")
        self.arkaplanda_calis = QCheckBox("Arkaplanda çalışmaya devam et")
        
        genel_layout.addWidget(self.otomatik_baslat)
        genel_layout.addWidget(self.arkaplanda_calis)
        
        genel_grup.setLayout(genel_layout)
        sistem_layout.addWidget(genel_grup)
        
        # Veri temizleme grubu
        temizlik_grup = QGroupBox("Veri Temizleme")
        temizlik_layout = QFormLayout()
        
        self.log_tutma = QSpinBox()
        self.log_tutma.setRange(1, 365)
        temizlik_layout.addRow("Log Tutma Süresi (gün):", self.log_tutma)
        
        self.veri_temizleme = QSpinBox()
        self.veri_temizleme.setRange(30, 365)
        temizlik_layout.addRow("Veri Temizleme Süresi (gün):", self.veri_temizleme)
        
        temizlik_grup.setLayout(temizlik_layout)
        sistem_layout.addWidget(temizlik_grup)
        
        sistem_layout.addStretch()
        self.tab_widget.addTab(sistem_widget, "Sistem")
    
    def _ayarlari_guncelle(self):
        """Widget'ları mevcut ayarlarla günceller."""
        # Email ayarları
        self.email_aktif.setChecked(self.ayarlar['email']['aktif'])
        self.smtp_sunucu.setText(self.ayarlar['email']['smtp_sunucu'])
        self.smtp_port.setValue(self.ayarlar['email']['smtp_port'])
        self.gonderen_email.setText(self.ayarlar['email']['gonderen_email'])
        self.gonderen_sifre.setText(self.ayarlar['email']['gonderen_sifre'])
        self.alici_email.setText(self.ayarlar['email']['alici_email'])
        
        # Masaüstü bildirimleri
        self.masaustu_aktif.setChecked(self.ayarlar['masaustu_bildirimleri']['aktif'])
        self.kritik_tehditler.setChecked(self.ayarlar['masaustu_bildirimleri']['kritik_tehditler'])
        self.sistem_durumlari.setChecked(self.ayarlar['masaustu_bildirimleri']['sistem_durumlari'])
        
        # Bildirim aralıkları
        self.kritik_aralik.setValue(self.ayarlar['bildirim_araligi']['kritik_tehditler'])
        self.normal_aralik.setValue(self.ayarlar['bildirim_araligi']['normal_tehditler'])
        self.sistem_aralik.setValue(self.ayarlar['bildirim_araligi']['sistem_durumlari'])
        
        # Sistem ayarları
        self.otomatik_baslat.setChecked(self.ayarlar['sistem']['otomatik_baslat'])
        self.arkaplanda_calis.setChecked(self.ayarlar['sistem']['arkaplanda_calis'])
        self.log_tutma.setValue(self.ayarlar['sistem']['log_tutma_suresi'])
        self.veri_temizleme.setValue(self.ayarlar['sistem']['veri_temizleme_suresi'])
    
    def _ayarlari_kaydet(self):
        """Ayarları kaydeder."""
        try:
            yeni_ayarlar = {
                'email': {
                    'aktif': self.email_aktif.isChecked(),
                    'smtp_sunucu': self.smtp_sunucu.text(),
                    'smtp_port': self.smtp_port.value(),
                    'gonderen_email': self.gonderen_email.text(),
                    'gonderen_sifre': self.gonderen_sifre.text(),
                    'alici_email': self.alici_email.text()
                },
                'masaustu_bildirimleri': {
                    'aktif': self.masaustu_aktif.isChecked(),
                    'kritik_tehditler': self.kritik_tehditler.isChecked(),
                    'sistem_durumlari': self.sistem_durumlari.isChecked()
                },
                'bildirim_araligi': {
                    'kritik_tehditler': self.kritik_aralik.value(),
                    'normal_tehditler': self.normal_aralik.value(),
                    'sistem_durumlari': self.sistem_aralik.value()
                },
                'sistem': {
                    'otomatik_baslat': self.otomatik_baslat.isChecked(),
                    'arkaplanda_calis': self.arkaplanda_calis.isChecked(),
                    'log_tutma_suresi': self.log_tutma.value(),
                    'veri_temizleme_suresi': self.veri_temizleme.value()
                }
            }
            
            # Ayarlar dizinini oluştur
            ayarlar_dizini = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
            os.makedirs(ayarlar_dizini, exist_ok=True)
            
            # Ayarları dosyaya kaydet
            ayarlar_dosyasi = os.path.join(ayarlar_dizini, 'settings.json')
            with open(ayarlar_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(yeni_ayarlar, f, indent=4, ensure_ascii=False)
            
            self.ayarlar = yeni_ayarlar
            self.ayarlar_degisti.emit(yeni_ayarlar)
            
            QMessageBox.information(
                self,
                "Başarılı",
                "Ayarlar başarıyla kaydedildi."
            )
            
            logger.info("Ayarlar güncellendi")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Ayarlar kaydedilirken hata oluştu: {e}"
            )
            logger.error(f"Ayarlar kaydedilirken hata: {e}") 