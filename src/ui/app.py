#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import os
from loguru import logger
from .main_window import AnaEkran

def uygulama_baslat():
    """ThreatTracker uygulamasını başlatır."""
    try:
        # Log dosyası yapılandırması
        log_dizini = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dizini, exist_ok=True)
        log_dosyasi = os.path.join(log_dizini, 'threattracker.log')
        
        logger.add(log_dosyasi, 
                  rotation="1 day",
                  retention="30 days",
                  level="INFO")
        
        logger.info("ThreatTracker başlatılıyor...")
        
        # PyQt uygulamasını başlat
        app = QApplication(sys.argv)
        
        # Stil ayarları
        style = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #bbdefb;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """
        app.setStyleSheet(style)
        
        # Ana pencereyi oluştur
        ana_pencere = AnaEkran()
        
        # İkon ayarla (eğer varsa)
        ikon_yolu = os.path.join(os.path.dirname(__file__), 
                                '..', '..', 'assets', 'icon.png')
        if os.path.exists(ikon_yolu):
            app.setWindowIcon(QIcon(ikon_yolu))
        
        # Pencereyi göster
        ana_pencere.show()
        
        logger.info("ThreatTracker arayüzü başlatıldı")
        
        # Uygulama döngüsünü başlat
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Uygulama başlatılırken hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    uygulama_baslat() 