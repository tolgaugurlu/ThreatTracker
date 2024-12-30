#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
import numpy as np
from src.ml.anomaly_detector import AnomaliTespitEdici

@pytest.fixture
def anomali_tespitedici():
    """Test için AnomaliTespitEdici örneği oluşturur."""
    return AnomaliTespitEdici(model_dizini="test_models")

@pytest.fixture
def ornek_sistem_durumlari():
    """Test için örnek sistem durumu verileri oluşturur."""
    return [
        {
            'cpu_kullanimi': 30.0,
            'ram_kullanimi': 45.0,
            'disk_kullanimi': 60.0,
            'aktif_baglanti_sayisi': 100
        },
        {
            'cpu_kullanimi': 40.0,
            'ram_kullanimi': 55.0,
            'disk_kullanimi': 65.0,
            'aktif_baglanti_sayisi': 150
        },
        # Anormal durumlar
        {
            'cpu_kullanimi': 95.0,
            'ram_kullanimi': 90.0,
            'disk_kullanimi': 95.0,
            'aktif_baglanti_sayisi': 2000
        }
    ]

def test_veri_hazirlama(anomali_tespitedici, ornek_sistem_durumlari):
    """Veri hazırlama fonksiyonunu test eder."""
    X = anomali_tespitedici.veri_hazirla(ornek_sistem_durumlari)
    assert isinstance(X, np.ndarray)
    assert X.shape == (3, 4)  # 3 örnek, 4 özellik

def test_model_egitme_ve_kaydetme(anomali_tespitedici, ornek_sistem_durumlari):
    """Model eğitme ve kaydetme işlemlerini test eder."""
    anomali_tespitedici.model_egit(ornek_sistem_durumlari)
    
    # Model dosyalarının oluşturulduğunu kontrol et
    assert os.path.exists(os.path.join("test_models", "isolation_forest.joblib"))
    assert os.path.exists(os.path.join("test_models", "one_class_svm.joblib"))
    assert os.path.exists(os.path.join("test_models", "scaler.joblib"))

def test_model_yukleme(anomali_tespitedici, ornek_sistem_durumlari):
    """Model yükleme işlemini test eder."""
    # Önce modeli eğit ve kaydet
    anomali_tespitedici.model_egit(ornek_sistem_durumlari)
    
    # Yeni bir tespitedici oluştur ve modeli yükle
    yeni_tespitedici = AnomaliTespitEdici(model_dizini="test_models")
    basarili = yeni_tespitedici.model_yukle()
    assert basarili == True

def test_normal_durum_tespiti(anomali_tespitedici, ornek_sistem_durumlari):
    """Normal sistem durumu tespitini test eder."""
    # Modeli eğit
    anomali_tespitedici.model_egit(ornek_sistem_durumlari)
    
    # Normal bir durum test et
    normal_durum = {
        'cpu_kullanimi': 35.0,
        'ram_kullanimi': 50.0,
        'disk_kullanimi': 62.0,
        'aktif_baglanti_sayisi': 120
    }
    
    anomali_var, skor, aciklama = anomali_tespitedici.anomali_tespit_et(normal_durum)
    assert anomali_var == False
    assert 0 <= skor <= 1
    assert "Normal sistem davranışı" in aciklama

def test_anomali_tespiti(anomali_tespitedici, ornek_sistem_durumlari):
    """Anormal sistem durumu tespitini test eder."""
    # Modeli eğit
    anomali_tespitedici.model_egit(ornek_sistem_durumlari)
    
    # Anormal bir durum test et
    anormal_durum = {
        'cpu_kullanimi': 95.0,
        'ram_kullanimi': 92.0,
        'disk_kullanimi': 98.0,
        'aktif_baglanti_sayisi': 3000
    }
    
    anomali_var, skor, aciklama = anomali_tespitedici.anomali_tespit_et(anormal_durum)
    assert anomali_var == True
    assert 0 <= skor <= 1
    assert "Yüksek CPU kullanımı" in aciklama
    assert "Yüksek RAM kullanımı" in aciklama
    assert "Kritik disk kullanımı" in aciklama
    assert "Yüksek bağlantı sayısı" in aciklama

def teardown_module(module):
    """Test sonrası temizlik işlemleri."""
    import shutil
    if os.path.exists("test_models"):
        shutil.rmtree("test_models") 