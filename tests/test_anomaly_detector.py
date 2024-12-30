#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import numpy as np
from src.ml.anomaly_detector import AnomalyDetector

@pytest.fixture
def anomaly_detector():
    """Test için AnomalyDetector örneği oluşturur."""
    return AnomalyDetector()

def test_ozellikleri_cikar(anomaly_detector):
    """_ozellikleri_cikar metodunu test eder."""
    ag_trafigi = {
        'paket_sayisi': 100,
        'bayt_sayisi': 1500,
        'ortalama_paket_boyutu': 150,
        'paket_aralik_suresi': 0.1,
        'protokol_turu': 6,  # TCP
        'port_numarasi': 80,
        'baglanti_suresi': 5.0
    }
    
    ozellikler = anomaly_detector._ozellikleri_cikar(ag_trafigi)
    
    assert len(ozellikler) == 7
    assert ozellikler[0] == 100.0
    assert ozellikler[1] == 1500.0
    assert ozellikler[2] == 150.0
    assert ozellikler[3] == 0.1
    assert ozellikler[4] == 6.0
    assert ozellikler[5] == 80.0
    assert ozellikler[6] == 5.0

def test_egit(anomaly_detector):
    """egit metodunu test eder."""
    egitim_verileri = [
        {
            'paket_sayisi': 100,
            'bayt_sayisi': 1500,
            'ortalama_paket_boyutu': 150,
            'paket_aralik_suresi': 0.1,
            'protokol_turu': 6,
            'port_numarasi': 80,
            'baglanti_suresi': 5.0
        },
        {
            'paket_sayisi': 200,
            'bayt_sayisi': 3000,
            'ortalama_paket_boyutu': 150,
            'paket_aralik_suresi': 0.2,
            'protokol_turu': 17,  # UDP
            'port_numarasi': 443,
            'baglanti_suresi': 10.0
        }
    ]
    
    anomaly_detector.egit(egitim_verileri)
    assert anomaly_detector.model is not None

def test_anomali_tespit_et(anomaly_detector):
    """anomali_tespit_et metodunu test eder."""
    # Önce modeli eğit
    egitim_verileri = [
        {
            'paket_sayisi': 100,
            'bayt_sayisi': 1500,
            'ortalama_paket_boyutu': 150,
            'paket_aralik_suresi': 0.1,
            'protokol_turu': 6,
            'port_numarasi': 80,
            'baglanti_suresi': 5.0
        } for _ in range(100)  # 100 normal örnek
    ]
    anomaly_detector.egit(egitim_verileri)
    
    # Normal trafik
    normal_trafik = {
        'paket_sayisi': 150,
        'bayt_sayisi': 2000,
        'ortalama_paket_boyutu': 150,
        'paket_aralik_suresi': 0.15,
        'protokol_turu': 6,
        'port_numarasi': 80,
        'baglanti_suresi': 7.0
    }
    
    # Anormal trafik (çok yüksek paket sayısı)
    anormal_trafik = {
        'paket_sayisi': 10000,
        'bayt_sayisi': 150000,
        'ortalama_paket_boyutu': 150,
        'paket_aralik_suresi': 0.01,
        'protokol_turu': 6,
        'port_numarasi': 80,
        'baglanti_suresi': 5.0
    }
    
    # Test et
    normal_sonuc, normal_skor = anomaly_detector.anomali_tespit_et(normal_trafik)
    anormal_sonuc, anormal_skor = anomaly_detector.anomali_tespit_et(anormal_trafik)
    
    assert not normal_sonuc  # Normal trafik için False
    assert normal_skor < 0.8  # Normal trafik için düşük skor
    assert anormal_sonuc  # Anormal trafik için True
    assert anormal_skor > 0.8  # Anormal trafik için yüksek skor

def test_anomali_raporu_olustur(anomaly_detector):
    """anomali_raporu_olustur metodunu test eder."""
    ag_trafigi = {
        'paket_sayisi': 10000,  # Anormal yüksek
        'bayt_sayisi': 150000,
        'ortalama_paket_boyutu': 150,
        'paket_aralik_suresi': 0.01,
        'protokol_turu': 6,
        'port_numarasi': 80,
        'baglanti_suresi': 5.0
    }
    
    rapor = anomaly_detector.anomali_raporu_olustur(
        ag_trafigi,
        anomali_var=True,
        anomali_skoru=0.95
    )
    
    assert isinstance(rapor, dict)
    assert rapor['anomali_var'] is True
    assert float(rapor['anomali_skoru']) == 0.95
    assert rapor['risk_seviyesi'] == 'YÜKSEK'
    assert rapor['anomali_turu'] == 'Yüksek Paket Sayısı (Olası DoS)'
    assert isinstance(rapor['oneriler'], list)
    assert len(rapor['oneriler']) > 0

def test_anomali_onerileri_olustur(anomaly_detector):
    """_anomali_onerileri_olustur metodunu test eder."""
    oneriler = anomaly_detector._anomali_onerileri_olustur('Yüksek Paket Sayısı (Olası DoS)')
    
    assert isinstance(oneriler, list)
    assert len(oneriler) == 3
    assert "Güvenlik duvarı kurallarını gözden geçirin" in oneriler
    assert "Rate limiting uygulayın" in oneriler
    assert "DDoS koruma servisleri kullanmayı değerlendirin" in oneriler 