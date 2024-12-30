#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Çalışma dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import AnaEkran

def main():
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur
    ana_ekran = AnaEkran()
    ana_ekran.show()
    
    # Uygulamayı başlat
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 