#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
import json
from datetime import datetime, timedelta
from src.utils.notifier import BildirimYoneticisi
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_config():
    """Test için örnek konfigürasyon dosyası oluşturur."""
    config = {
        'email': {
            'aktif': True,
            'smtp_sunucu': 'smtp.test.com',
            'smtp_port': 587,
            'gonderen_email': 'test@test.com',
            'gonderen_sifre': 'test123',
            'alici_email': 'alici@test.com'
        },
        'masaustu_bildirimleri': {
            'aktif': True,
            'kritik_tehditler': True,
            'sistem_durumlari': True
        },
        'bildirim_araligi': {
            'kritik_tehditler': 60,
            'normal_tehditler': 300,
            'sistem_durumlari': 600
        }
    }
    
    with open('test_config.json', 'w') as f:
        json.dump(config, f)
    
    yield 'test_config.json'
    
    if os.path.exists('test_config.json'):
        os.remove('test_config.json')

@pytest.fixture
def bildirim_yoneticisi(test_config):
    """Test için BildirimYoneticisi örneği oluşturur."""
    return BildirimYoneticisi(test_config)

def test_config_yukleme(test_config):
    """Konfigürasyon yükleme işlemini test eder."""
    yonetici = BildirimYoneticisi(test_config)
    assert yonetici.config['email']['smtp_sunucu'] == 'smtp.test.com'
    assert yonetici.config['email']['smtp_port'] == 587
    assert yonetici.config['masaustu_bildirimleri']['aktif'] == True

@patch('smtplib.SMTP')
def test_email_gonderme(mock_smtp, bildirim_yoneticisi):
    """Email gönderme işlemini test eder."""
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value = mock_smtp_instance
    
    basarili = bildirim_yoneticisi.email_gonder(
        "Test Konusu",
        "Test Mesajı",
        "kritik"
    )
    
    assert basarili == True
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once()
    mock_smtp_instance.send_message.assert_called_once()
    mock_smtp_instance.quit.assert_called_once()

@patch('subprocess.run')
def test_masaustu_bildirim_gonderme(mock_run, bildirim_yoneticisi):
    """Masaüstü bildirimi gönderme işlemini test eder."""
    basarili = bildirim_yoneticisi.masaustu_bildirim_gonder(
        "Test Başlığı",
        "Test Mesajı"
    )
    
    assert basarili == True
    mock_run.assert_called_once()

def test_tehdit_bildirimi_gonderme(bildirim_yoneticisi):
    """Tehdit bildirimi gönderme işlemini test eder."""
    with patch.object(bildirim_yoneticisi, 'email_gonder') as mock_email:
        with patch.object(bildirim_yoneticisi, 'masaustu_bildirim_gonder') as mock_masaustu:
            # Kritik tehdit bildirimi
            tehdit = {
                'id': 1,
                'tip': 'PORT_TARAMA',
                'onem_derecesi': 4,
                'kaynak_ip': '192.168.1.100',
                'hedef_ip': '192.168.1.1',
                'detaylar': {'port_sayisi': 100}
            }
            
            bildirim_yoneticisi.tehdit_bildirimi_gonder(tehdit)
            
            mock_email.assert_called_once()
            mock_masaustu.assert_called_once()
            
            # Aynı tehdit için tekrar bildirim gönderme denemesi
            mock_email.reset_mock()
            mock_masaustu.reset_mock()
            
            bildirim_yoneticisi.tehdit_bildirimi_gonder(tehdit)
            
            # Bildirim aralığından dolayı çağrılmamalı
            mock_email.assert_not_called()
            mock_masaustu.assert_not_called()

def test_sistem_durumu_bildirimi_gonderme(bildirim_yoneticisi):
    """Sistem durumu bildirimi gönderme işlemini test eder."""
    with patch.object(bildirim_yoneticisi, 'email_gonder') as mock_email:
        with patch.object(bildirim_yoneticisi, 'masaustu_bildirim_gonder') as mock_masaustu:
            # Kritik sistem durumu
            durum = {
                'cpu_kullanimi': 95.0,
                'ram_kullanimi': 92.0,
                'disk_kullanimi': 98.0,
                'aktif_baglanti_sayisi': 1000
            }
            
            bildirim_yoneticisi.sistem_durumu_bildirimi_gonder(durum)
            
            mock_email.assert_called_once()
            mock_masaustu.assert_called_once()
            
            # Normal sistem durumu
            mock_email.reset_mock()
            mock_masaustu.reset_mock()
            
            durum = {
                'cpu_kullanimi': 50.0,
                'ram_kullanimi': 60.0,
                'disk_kullanimi': 70.0,
                'aktif_baglanti_sayisi': 100
            }
            
            bildirim_yoneticisi.sistem_durumu_bildirimi_gonder(durum)
            
            mock_email.assert_not_called()  # Normal durum için email gönderilmemeli
            mock_masaustu.assert_called_once() 