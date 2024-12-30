#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os
from PyQt6.QtWidgets import QApplication
from src.main import main

def test_main_fonksiyonu(qtbot, tmp_path):
    """Ana fonksiyonun çalışmasını test eder."""
    # Log dizinini geçici dizine yönlendir
    os.environ['LOG_DIR'] = str(tmp_path)
    
    # QApplication örneği oluştur
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Ana fonksiyonu çağır
        main()
        assert True  # Hata oluşmadan çalıştıysa başarılı
        
    except SystemExit as e:
        # sys.exit() çağrısı yapıldığında SystemExit hatası oluşur
        # Bu beklenen bir durum
        assert e.code in [0, None]  # Başarılı çıkış
        
    finally:
        # Test sonrası temizlik
        if os.path.exists(str(tmp_path)):
            for f in os.listdir(str(tmp_path)):
                os.remove(os.path.join(str(tmp_path), f))

def test_log_dosyasi_olusturma(tmp_path):
    """Log dosyasının oluşturulmasını test eder."""
    # Log dizinini geçici dizine yönlendir
    log_dizini = tmp_path / "logs"
    os.environ['LOG_DIR'] = str(log_dizini)
    
    # QApplication örneği oluştur
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Ana fonksiyonu çağır
        main()
        
    except SystemExit:
        pass
    
    finally:
        # Log dosyasının oluşturulduğunu kontrol et
        assert os.path.exists(log_dizini)
        log_dosyalari = os.listdir(log_dizini)
        assert len(log_dosyalari) > 0
        assert any(f.startswith("threattracker") for f in log_dosyalari)
        
        # Test sonrası temizlik
        for f in log_dosyalari:
            os.remove(os.path.join(log_dizini, f))
        os.rmdir(log_dizini) 