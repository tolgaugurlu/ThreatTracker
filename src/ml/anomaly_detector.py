#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
import os
from loguru import logger

class AnomaliTespitEdici:
    """Sistem metriklerinde anomali tespiti yapan sınıf."""
    
    def __init__(self, model_dizini: str = None):
        """
        Args:
            model_dizini: Eğitilmiş modellerin kaydedileceği dizin
        """
        if model_dizini is None:
            model_dizini = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        os.makedirs(model_dizini, exist_ok=True)
        
        self.model_dizini = model_dizini
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.one_class_svm = OneClassSVM(
            kernel='rbf',
            nu=0.1
        )
        
        logger.info("AnomaliTespitEdici başlatıldı")
    
    def veri_hazirla(self, sistem_durumlari: List[Dict]) -> np.ndarray:
        """Ham sistem durumu verilerini ML modeli için hazırlar.
        
        Args:
            sistem_durumlari: Sistem durumu kayıtları
            
        Returns:
            np.ndarray: Hazırlanmış özellik matrisi
        """
        df = pd.DataFrame(sistem_durumlari)
        
        # Temel özellikleri seç
        ozellikler = [
            'cpu_kullanimi',
            'ram_kullanimi',
            'disk_kullanimi',
            'aktif_baglanti_sayisi'
        ]
        
        X = df[ozellikler].values
        return self.scaler.fit_transform(X)
    
    def model_egit(self, sistem_durumlari: List[Dict]) -> None:
        """Anomali tespit modellerini eğitir.
        
        Args:
            sistem_durumlari: Eğitim için kullanılacak sistem durumu kayıtları
        """
        X = self.veri_hazirla(sistem_durumlari)
        
        # Modelleri eğit
        self.isolation_forest.fit(X)
        self.one_class_svm.fit(X)
        
        # Modelleri kaydet
        joblib.dump(self.isolation_forest, 
                   os.path.join(self.model_dizini, 'isolation_forest.joblib'))
        joblib.dump(self.one_class_svm,
                   os.path.join(self.model_dizini, 'one_class_svm.joblib'))
        joblib.dump(self.scaler,
                   os.path.join(self.model_dizini, 'scaler.joblib'))
        
        logger.info("Anomali tespit modelleri eğitildi ve kaydedildi")
    
    def model_yukle(self) -> bool:
        """Kaydedilmiş modelleri yükler.
        
        Returns:
            bool: Modeller başarıyla yüklendiyse True
        """
        try:
            self.isolation_forest = joblib.load(
                os.path.join(self.model_dizini, 'isolation_forest.joblib'))
            self.one_class_svm = joblib.load(
                os.path.join(self.model_dizini, 'one_class_svm.joblib'))
            self.scaler = joblib.load(
                os.path.join(self.model_dizini, 'scaler.joblib'))
            logger.info("Kaydedilmiş modeller yüklendi")
            return True
        except:
            logger.warning("Kaydedilmiş modeller yüklenemedi")
            return False
    
    def anomali_tespit_et(self, sistem_durumu: Dict) -> Tuple[bool, float, str]:
        """Tek bir sistem durumu için anomali tespiti yapar.
        
        Args:
            sistem_durumu: Analiz edilecek sistem durumu
            
        Returns:
            Tuple[bool, float, str]: (Anomali var mı, Anomali skoru, Açıklama)
        """
        # Veriyi hazırla
        X = self.scaler.transform([[
            sistem_durumu['cpu_kullanimi'],
            sistem_durumu['ram_kullanimi'],
            sistem_durumu['disk_kullanimi'],
            sistem_durumu['aktif_baglanti_sayisi']
        ]])
        
        # Her iki model ile tahmin yap
        if_pred = self.isolation_forest.predict(X)[0]
        svm_pred = self.one_class_svm.predict(X)[0]
        
        # Anomali skorlarını hesapla (-1: anomali, 1: normal)
        if_score = self.isolation_forest.score_samples(X)[0]
        svm_score = self.one_class_svm.score_samples(X)[0]
        
        # Ortalama anomali skoru (0-1 arasına normalize et)
        anomali_skoru = 1 - (if_score + svm_score + 2) / 4
        
        # Her iki model de anomali tespit ettiyse
        if if_pred == -1 and svm_pred == -1:
            aciklama = self._anomali_aciklamasi_olustur(sistem_durumu, anomali_skoru)
            logger.warning(f"Kritik anomali tespit edildi: {aciklama}")
            return True, anomali_skoru, aciklama
        
        # Sadece bir model anomali tespit ettiyse
        elif if_pred == -1 or svm_pred == -1:
            aciklama = self._anomali_aciklamasi_olustur(sistem_durumu, anomali_skoru)
            logger.info(f"Olası anomali tespit edildi: {aciklama}")
            return True, anomali_skoru, aciklama
        
        return False, anomali_skoru, "Normal sistem davranışı"
    
    def _anomali_aciklamasi_olustur(self, sistem_durumu: Dict, 
                                   anomali_skoru: float) -> str:
        """Anomali için açıklayıcı bir mesaj oluşturur.
        
        Args:
            sistem_durumu: Analiz edilen sistem durumu
            anomali_skoru: Hesaplanan anomali skoru
            
        Returns:
            str: Açıklayıcı mesaj
        """
        nedenler = []
        
        if sistem_durumu['cpu_kullanimi'] > 80:
            nedenler.append(f"Yüksek CPU kullanımı (%{sistem_durumu['cpu_kullanimi']:.1f})")
        
        if sistem_durumu['ram_kullanimi'] > 80:
            nedenler.append(f"Yüksek RAM kullanımı (%{sistem_durumu['ram_kullanimi']:.1f})")
        
        if sistem_durumu['disk_kullanimi'] > 90:
            nedenler.append(f"Kritik disk kullanımı (%{sistem_durumu['disk_kullanimi']:.1f})")
        
        if sistem_durumu['aktif_baglanti_sayisi'] > 1000:
            nedenler.append(f"Yüksek bağlantı sayısı ({sistem_durumu['aktif_baglanti_sayisi']})")
        
        if nedenler:
            return f"Anomali skoru: {anomali_skoru:.2f}. Nedenler: {', '.join(nedenler)}"
        else:
            return f"Anomali skoru: {anomali_skoru:.2f}. Beklenmeyen sistem davranışı" 