#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from typing import List, Dict, Tuple
from loguru import logger

class AnomalyDetector:
    """Anomali tespiti sınıfı."""
    
    def __init__(self):
        """AnomalyDetector sınıfının başlatıcısı."""
        self.model = None
        self.scaler = StandardScaler()
        self.ozellikler = [
            'paket_sayisi',
            'bayt_sayisi',
            'ortalama_paket_boyutu',
            'paket_aralik_suresi',
            'protokol_turu',
            'port_numarasi',
            'baglanti_suresi'
        ]
        
        # Modeli yükle veya yeni model oluştur
        self._modeli_yukle()
    
    def _modeli_yukle(self):
        """Kaydedilmiş modeli yükler veya yeni model oluşturur."""
        try:
            model_dosyasi = os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'data',
                'anomaly_model.joblib'
            )
            
            if os.path.exists(model_dosyasi):
                self.model = joblib.load(model_dosyasi)
                logger.info("Anomali tespit modeli yüklendi")
            else:
                self.model = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                logger.info("Yeni anomali tespit modeli oluşturuldu")
            
        except Exception as e:
            logger.error(f"Model yüklenirken hata: {e}")
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42
            )
    
    def _modeli_kaydet(self):
        """Modeli dosyaya kaydeder."""
        try:
            model_dizini = os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'data'
            )
            os.makedirs(model_dizini, exist_ok=True)
            
            model_dosyasi = os.path.join(
                model_dizini,
                'anomaly_model.joblib'
            )
            
            joblib.dump(self.model, model_dosyasi)
            logger.info("Anomali tespit modeli kaydedildi")
            
        except Exception as e:
            logger.error(f"Model kaydedilirken hata: {e}")
    
    def _ozellikleri_cikar(self, ag_trafigi: Dict) -> List[float]:
        """Ağ trafiği verilerinden özellik vektörü oluşturur.
        
        Args:
            ag_trafigi: Ağ trafiği verileri
            
        Returns:
            List[float]: Özellik vektörü
        """
        return [
            float(ag_trafigi.get('paket_sayisi', 0)),
            float(ag_trafigi.get('bayt_sayisi', 0)),
            float(ag_trafigi.get('ortalama_paket_boyutu', 0)),
            float(ag_trafigi.get('paket_aralik_suresi', 0)),
            float(ag_trafigi.get('protokol_turu', 0)),
            float(ag_trafigi.get('port_numarasi', 0)),
            float(ag_trafigi.get('baglanti_suresi', 0))
        ]
    
    def egit(self, egitim_verileri: List[Dict]):
        """Modeli eğitir.
        
        Args:
            egitim_verileri: Eğitim verileri listesi
        """
        try:
            # Özellik matrisi oluştur
            X = np.array([
                self._ozellikleri_cikar(veri)
                for veri in egitim_verileri
            ])
            
            # Verileri normalize et
            X_norm = self.scaler.fit_transform(X)
            
            # Modeli eğit
            self.model.fit(X_norm)
            
            # Modeli kaydet
            self._modeli_kaydet()
            
            logger.info(f"{len(egitim_verileri)} örnek ile model eğitildi")
            
        except Exception as e:
            logger.error(f"Model eğitilirken hata: {e}")
    
    def anomali_tespit_et(self, ag_trafigi: Dict) -> Tuple[bool, float]:
        """Ağ trafiğinde anomali olup olmadığını tespit eder.
        
        Args:
            ag_trafigi: Ağ trafiği verileri
            
        Returns:
            Tuple[bool, float]: (Anomali var mı?, Anomali skoru)
        """
        try:
            # Özellik vektörü oluştur
            X = np.array([self._ozellikleri_cikar(ag_trafigi)])
            
            # Verileri normalize et
            X_norm = self.scaler.transform(X)
            
            # Anomali skoru hesapla (-1: anomali, 1: normal)
            skor = self.model.score_samples(X_norm)[0]
            
            # Skoru 0-1 aralığına normalize et
            normalize_skor = 1 - (skor + 1) / 2
            
            # Anomali tespiti (skor < 0 ise anomali)
            return normalize_skor > 0.8, normalize_skor
            
        except Exception as e:
            logger.error(f"Anomali tespiti yapılırken hata: {e}")
            return False, 0.0
    
    def anomali_raporu_olustur(self, ag_trafigi: Dict, 
                              anomali_var: bool, 
                              anomali_skoru: float) -> Dict:
        """Anomali raporu oluşturur.
        
        Args:
            ag_trafigi: Ağ trafiği verileri
            anomali_var: Anomali var mı?
            anomali_skoru: Anomali skoru
            
        Returns:
            Dict: Anomali raporu
        """
        try:
            rapor = {
                'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'anomali_var': anomali_var,
                'anomali_skoru': f"{anomali_skoru:.2f}",
                'risk_seviyesi': 'YÜKSEK' if anomali_skoru > 0.9 else 'ORTA' if anomali_skoru > 0.8 else 'DÜŞÜK',
                'detaylar': {
                    'paket_sayisi': ag_trafigi.get('paket_sayisi', 0),
                    'bayt_sayisi': ag_trafigi.get('bayt_sayisi', 0),
                    'ortalama_paket_boyutu': ag_trafigi.get('ortalama_paket_boyutu', 0),
                    'protokol': ag_trafigi.get('protokol_turu', 'Bilinmiyor'),
                    'port': ag_trafigi.get('port_numarasi', 0)
                }
            }
            
            # Anomali türünü belirle
            if anomali_var:
                if ag_trafigi.get('paket_sayisi', 0) > 1000:
                    rapor['anomali_turu'] = 'Yüksek Paket Sayısı (Olası DoS)'
                elif ag_trafigi.get('port_numarasi', 0) > 49151:
                    rapor['anomali_turu'] = 'Şüpheli Port Kullanımı'
                elif ag_trafigi.get('ortalama_paket_boyutu', 0) > 1500:
                    rapor['anomali_turu'] = 'Anormal Paket Boyutu'
                else:
                    rapor['anomali_turu'] = 'Bilinmeyen Anomali'
                
                rapor['oneriler'] = self._anomali_onerileri_olustur(rapor['anomali_turu'])
            
            return rapor
            
        except Exception as e:
            logger.error(f"Anomali raporu oluşturulurken hata: {e}")
            return {}
    
    def _anomali_onerileri_olustur(self, anomali_turu: str) -> List[str]:
        """Anomali türüne göre öneriler oluşturur.
        
        Args:
            anomali_turu: Anomali türü
            
        Returns:
            List[str]: Öneriler listesi
        """
        oneriler = {
            'Yüksek Paket Sayısı (Olası DoS)': [
                "Güvenlik duvarı kurallarını gözden geçirin",
                "Rate limiting uygulayın",
                "DDoS koruma servisleri kullanmayı değerlendirin"
            ],
            'Şüpheli Port Kullanımı': [
                "Kullanılmayan portları kapatın",
                "Port taraması yaparak açık portları kontrol edin",
                "Güvenlik duvarı kurallarını sıkılaştırın"
            ],
            'Anormal Paket Boyutu': [
                "MTU değerlerini kontrol edin",
                "Paket fragmentasyonunu izleyin",
                "Deep packet inspection yapın"
            ],
            'Bilinmeyen Anomali': [
                "Sistem loglarını detaylı inceleyin",
                "Ağ trafiğini monitör edin",
                "Güvenlik yazılımlarını güncelleyin"
            ]
        }
        
        return oneriler.get(anomali_turu, ["Sistem yöneticinize başvurun"]) 