#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
from datetime import datetime
from src.core.models import (
    VeritabaniYoneticisi, TehditTipi, Tehdit, Olay, SistemDurumu
)

@pytest.fixture
def db_yonetici():
    """Test için geçici bir SQLite veritabanı oluşturur."""
    test_db_path = "test_threattracker.db"
    db = VeritabaniYoneticisi(f"sqlite:///{test_db_path}")
    db.init_db()
    yield db
    # Temizlik
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_tehdit_kaydetme(db_yonetici):
    """Tehdit kaydetme işlemini test eder."""
    tehdit = db_yonetici.kaydet_tehdit(
        tip=TehditTipi.PORT_TARAMA,
        kaynak_ip="192.168.1.100",
        hedef_ip="192.168.1.1",
        detaylar={"port_sayisi": 100},
        onem_derecesi=3
    )
    
    assert tehdit.id is not None
    assert tehdit.tip == TehditTipi.PORT_TARAMA
    assert tehdit.kaynak_ip == "192.168.1.100"
    assert tehdit.onem_derecesi == 3
    assert tehdit.detaylar["port_sayisi"] == 100

def test_olay_kaydetme(db_yonetici):
    """Olay kaydetme işlemini test eder."""
    # Önce bir tehdit oluştur
    tehdit = db_yonetici.kaydet_tehdit(
        tip=TehditTipi.DDOS,
        kaynak_ip="192.168.1.100"
    )
    
    # Olayı kaydet
    olay = db_yonetici.kaydet_olay(
        tip="Network",
        kaynak="IDS",
        mesaj="Şüpheli ağ trafiği tespit edildi",
        tehdit_id=tehdit.id,
        detaylar={"paket_sayisi": 1000}
    )
    
    assert olay.id is not None
    assert olay.tehdit_id == tehdit.id
    assert olay.tip == "Network"
    assert olay.detaylar["paket_sayisi"] == 1000

def test_sistem_durumu_kaydetme(db_yonetici):
    """Sistem durumu kaydetme işlemini test eder."""
    durum = db_yonetici.kaydet_sistem_durumu(
        cpu_kullanimi=45.5,
        ram_kullanimi=60.0,
        disk_kullanimi=75.2,
        aktif_baglanti_sayisi=100,
        detaylar={"islemci_sicakligi": 65}
    )
    
    assert durum.id is not None
    assert durum.cpu_kullanimi == 45.5
    assert durum.ram_kullanimi == 60.0
    assert durum.disk_kullanimi == 75.2
    assert durum.aktif_baglanti_sayisi == 100
    assert durum.detaylar["islemci_sicakligi"] == 65

def test_tehdit_to_dict(db_yonetici):
    """Tehdit nesnesinin sözlüğe dönüştürülmesini test eder."""
    tehdit = db_yonetici.kaydet_tehdit(
        tip=TehditTipi.SUSPICIOUS_PROCESS,
        kaynak_ip="192.168.1.100",
        detaylar={"cpu_kullanimi": 95}
    )
    
    tehdit_dict = tehdit.to_dict()
    assert tehdit_dict["tip"] == "suspicious_process"
    assert tehdit_dict["kaynak_ip"] == "192.168.1.100"
    assert tehdit_dict["detaylar"]["cpu_kullanimi"] == 95

def test_olay_to_dict(db_yonetici):
    """Olay nesnesinin sözlüğe dönüştürülmesini test eder."""
    olay = db_yonetici.kaydet_olay(
        tip="System",
        kaynak="ProcessMonitor",
        mesaj="Yüksek CPU kullanımı",
        detaylar={"cpu_kullanimi": 95}
    )
    
    olay_dict = olay.to_dict()
    assert olay_dict["tip"] == "System"
    assert olay_dict["kaynak"] == "ProcessMonitor"
    assert olay_dict["mesaj"] == "Yüksek CPU kullanımı"
    assert olay_dict["detaylar"]["cpu_kullanimi"] == 95 