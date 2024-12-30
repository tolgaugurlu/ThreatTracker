#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    """Test için QApplication örneği oluşturur."""
    test_app = QApplication([])
    return test_app

@pytest.fixture
def main_window(app, qtbot):
    """Test için MainWindow örneği oluşturur."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_pencere_basligi(main_window):
    """Pencere başlığını test eder."""
    assert main_window.windowTitle() == "ThreatTracker - Güvenlik İzleme Aracı"

def test_pencere_boyutu(main_window):
    """Pencere boyutunu test eder."""
    assert main_window.width() == 1200
    assert main_window.height() == 800

def test_durum_cubugu(main_window):
    """Durum çubuğunu test eder."""
    assert main_window.durum_cubugu.currentMessage() == "Hazır"

def test_tehditler_tablosu(main_window):
    """Tehditler tablosunu test eder."""
    assert main_window.tehditler_tablo.columnCount() == 5
    basliklar = [
        main_window.tehditler_tablo.horizontalHeaderItem(i).text()
        for i in range(5)
    ]
    assert basliklar == ["Zaman", "Tehdit", "Seviye", "Kaynak", "Durum"]

def test_surecler_tablosu(main_window):
    """Süreçler tablosunu test eder."""
    assert main_window.surecler_tablo.columnCount() == 5
    basliklar = [
        main_window.surecler_tablo.horizontalHeaderItem(i).text()
        for i in range(5)
    ]
    assert basliklar == ["PID", "İsim", "CPU %", "RAM %", "Durum"]

def test_baglantilar_tablosu(main_window):
    """Bağlantılar tablosunu test eder."""
    assert main_window.baglantilar_tablo.columnCount() == 5
    basliklar = [
        main_window.baglantilar_tablo.horizontalHeaderItem(i).text()
        for i in range(5)
    ]
    assert basliklar == ["Protokol", "Yerel Adres", "Uzak Adres", "Durum", "PID"]

def test_tehditleri_temizle(main_window, qtbot):
    """Tehditleri temizle fonksiyonunu test eder."""
    # Önce bir tehdit ekle
    main_window.tehditler_tablo.insertRow(0)
    main_window.tehditler_tablo.setItem(0, 0, QtWidgets.QTableWidgetItem("Test"))
    
    # Temizle butonuna tıkla
    qtbot.mouseClick(main_window.temizle_buton, Qt.MouseButton.LeftButton)
    
    # Tablonun boş olduğunu kontrol et
    assert main_window.tehditler_tablo.rowCount() == 0
    assert main_window.durum_cubugu.currentMessage() == "Tehdit listesi temizlendi"

def test_guvenlik_taramasi_baslat(main_window, qtbot):
    """Güvenlik taraması başlatma fonksiyonunu test eder."""
    # Tarama butonuna tıkla
    qtbot.mouseClick(main_window.tara_buton, Qt.MouseButton.LeftButton)
    
    # Butonun devre dışı olduğunu kontrol et
    assert not main_window.tara_buton.isEnabled()
    assert main_window.durum_cubugu.currentMessage() == "Güvenlik taraması başlatılıyor..."

def test_zamanlayicilar(main_window):
    """Zamanlayıcıları test eder."""
    assert main_window.sistem_zamanlayici.isActive()
    assert main_window.surec_zamanlayici.isActive()
    assert main_window.tehdit_zamanlayici.isActive()
    
    # Aralıkları kontrol et
    assert main_window.sistem_zamanlayici.interval() == 2000  # 2 saniye
    assert main_window.surec_zamanlayici.interval() == 5000  # 5 saniye
    assert main_window.tehdit_zamanlayici.interval() == 10000  # 10 saniye 