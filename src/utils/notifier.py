#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import json
import subprocess

class BildirimYoneticisi:
    """Tehdit ve sistem bildirimleri yöneten sınıf."""
    
    def __init__(self, config_file: str = None):
        """
        Args:
            config_file: Bildirim ayarları dosyası
        """
        self.config = self._config_yukle(config_file)
        self.son_bildirimler: Dict[str, datetime] = {}
        logger.info("BildirimYoneticisi başlatıldı")
    
    def _config_yukle(self, config_file: str = None) -> Dict:
        """Bildirim ayarlarını yükler.
        
        Args:
            config_file: Ayar dosyası yolu
            
        Returns:
            Dict: Ayarlar sözlüğü
        """
        default_config = {
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
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.error(f"Ayar dosyası yüklenirken hata: {e}")
        
        return default_config
    
    def email_gonder(self, konu: str, mesaj: str, onem: str = "normal") -> bool:
        """Email bildirimi gönderir.
        
        Args:
            konu: Email konusu
            mesaj: Email içeriği
            onem: Bildirimin önemi (kritik/normal)
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.config['email']['aktif']:
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['gonderen_email']
            msg['To'] = self.config['email']['alici_email']
            msg['Subject'] = f"[ThreatTracker] {konu}"
            
            body = f"""
            {mesaj}
            
            Bildirim Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Önem Derecesi: {onem.upper()}
            
            Bu email ThreatTracker güvenlik sistemi tarafından otomatik olarak gönderilmiştir.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.config['email']['smtp_sunucu'],
                self.config['email']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['email']['gonderen_email'],
                self.config['email']['gonderen_sifre']
            )
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email bildirimi gönderildi: {konu}")
            return True
            
        except Exception as e:
            logger.error(f"Email gönderilirken hata: {e}")
            return False
    
    def masaustu_bildirim_gonder(self, baslik: str, mesaj: str) -> bool:
        """Masaüstü bildirimi gönderir.
        
        Args:
            baslik: Bildirim başlığı
            mesaj: Bildirim mesajı
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.config['masaustu_bildirimleri']['aktif']:
            return False
            
        try:
            sistem = platform.system()
            
            if sistem == "Darwin":  # macOS
                komut = f'''
                osascript -e 'display notification "{mesaj}" with title "{baslik}"'
                '''
                subprocess.run(komut, shell=True)
                
            elif sistem == "Linux":
                komut = f'''
                notify-send "{baslik}" "{mesaj}"
                '''
                subprocess.run(komut, shell=True)
                
            elif sistem == "Windows":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(baslik, mesaj, duration=10)
            
            logger.info(f"Masaüstü bildirimi gönderildi: {baslik}")
            return True
            
        except Exception as e:
            logger.error(f"Masaüstü bildirimi gönderilirken hata: {e}")
            return False
    
    def tehdit_bildirimi_gonder(self, tehdit: Dict) -> None:
        """Tehdit bildirimi gönderir.
        
        Args:
            tehdit: Tehdit bilgileri
        """
        # Bildirim aralığını kontrol et
        tehdit_id = str(tehdit.get('id', ''))
        son_bildirim = self.son_bildirimler.get(tehdit_id)
        
        if son_bildirim:
            sure_farki = (datetime.now() - son_bildirim).total_seconds()
            if tehdit['onem_derecesi'] >= 4:  # Kritik tehdit
                if sure_farki < self.config['bildirim_araligi']['kritik_tehditler']:
                    return
            else:  # Normal tehdit
                if sure_farki < self.config['bildirim_araligi']['normal_tehditler']:
                    return
        
        # Bildirim başlığı ve mesajını oluştur
        baslik = f"Güvenlik Tehdidi: {tehdit['tip']}"
        mesaj = f"""
        Önem Derecesi: {tehdit['onem_derecesi']}/5
        Kaynak IP: {tehdit.get('kaynak_ip', 'Bilinmiyor')}
        Hedef IP: {tehdit.get('hedef_ip', 'Bilinmiyor')}
        Detaylar: {tehdit.get('detaylar', {})}
        """
        
        # Bildirimleri gönder
        if tehdit['onem_derecesi'] >= 4:  # Kritik tehdit
            self.email_gonder(baslik, mesaj, "kritik")
            self.masaustu_bildirim_gonder(f"⚠️ {baslik}", mesaj)
        else:
            self.masaustu_bildirim_gonder(f"ℹ️ {baslik}", mesaj)
        
        # Son bildirim zamanını güncelle
        self.son_bildirimler[tehdit_id] = datetime.now()
    
    def sistem_durumu_bildirimi_gonder(self, durum: Dict) -> None:
        """Sistem durumu bildirimi gönderir.
        
        Args:
            durum: Sistem durumu bilgileri
        """
        # Bildirim aralığını kontrol et
        if 'sistem_durumu' in self.son_bildirimler:
            sure_farki = (datetime.now() - self.son_bildirimler['sistem_durumu']).total_seconds()
            if sure_farki < self.config['bildirim_araligi']['sistem_durumlari']:
                return
        
        # Kritik durum kontrolü
        kritik_durum = (
            durum['cpu_kullanimi'] > 90 or
            durum['ram_kullanimi'] > 90 or
            durum['disk_kullanimi'] > 95
        )
        
        baslik = "Sistem Durumu" if not kritik_durum else "⚠️ Kritik Sistem Durumu"
        mesaj = f"""
        CPU Kullanımı: %{durum['cpu_kullanimi']:.1f}
        RAM Kullanımı: %{durum['ram_kullanimi']:.1f}
        Disk Kullanımı: %{durum['disk_kullanimi']:.1f}
        Aktif Bağlantı: {durum['aktif_baglanti_sayisi']}
        """
        
        if kritik_durum:
            self.email_gonder(baslik, mesaj, "kritik")
        
        if self.config['masaustu_bildirimleri']['sistem_durumlari']:
            self.masaustu_bildirim_gonder(baslik, mesaj)
        
        self.son_bildirimler['sistem_durumu'] = datetime.now() 