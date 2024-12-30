#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from loguru import logger

def main():
    """Ana uygulama fonksiyonu."""
    try:
        # Log ayarlarını yapılandır
        logger.add(
            "logs/threattracker.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        # Uygulamayı başlat
        app = QApplication(sys.argv)
        
        # Ana pencereyi oluştur
        ana_pencere = MainWindow()
        ana_pencere.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Uygulama başlatılırken hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 