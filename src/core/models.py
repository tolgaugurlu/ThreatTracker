#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import json
import os

Base = declarative_base()

class TehditTipi(enum.Enum):
    """Tehdit tiplerini tanımlayan enum sınıfı."""
    PORT_TARAMA = "port_tarama"
    DDOS = "ddos"
    SUSPICIOUS_PROCESS = "suspicious_process"
    ANOMALI = "anomali"
    DIGER = "diger"

class Tehdit(Base):
    """Tespit edilen tehditleri saklayan tablo."""
    __tablename__ = 'tehditler'
    
    id = Column(Integer, primary_key=True)
    tip = Column(Enum(TehditTipi), nullable=False)
    kaynak_ip = Column(String, nullable=True)
    hedef_ip = Column(String, nullable=True)
    tespit_zamani = Column(DateTime, default=datetime.now)
    onem_derecesi = Column(Integer, default=1)  # 1-5 arası
    detaylar = Column(JSON)
    durum = Column(String, default="Yeni")  # Yeni, İnceleniyor, Çözüldü
    
    olaylar = relationship("Olay", back_populates="tehdit")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tip': self.tip.value,
            'kaynak_ip': self.kaynak_ip,
            'hedef_ip': self.hedef_ip,
            'tespit_zamani': self.tespit_zamani.isoformat(),
            'onem_derecesi': self.onem_derecesi,
            'detaylar': self.detaylar,
            'durum': self.durum
        }

class Olay(Base):
    """Sistem olaylarını ve logları saklayan tablo."""
    __tablename__ = 'olaylar'
    
    id = Column(Integer, primary_key=True)
    tehdit_id = Column(Integer, ForeignKey('tehditler.id'), nullable=True)
    tip = Column(String, nullable=False)  # Process, Network, System
    kaynak = Column(String, nullable=False)
    mesaj = Column(String)
    zaman = Column(DateTime, default=datetime.now)
    detaylar = Column(JSON)
    
    tehdit = relationship("Tehdit", back_populates="olaylar")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tehdit_id': self.tehdit_id,
            'tip': self.tip,
            'kaynak': self.kaynak,
            'mesaj': self.mesaj,
            'zaman': self.zaman.isoformat(),
            'detaylar': self.detaylar
        }

class SistemDurumu(Base):
    """Sistem durumu metriklerini saklayan tablo."""
    __tablename__ = 'sistem_durumu'
    
    id = Column(Integer, primary_key=True)
    zaman = Column(DateTime, default=datetime.now)
    cpu_kullanimi = Column(Float)
    ram_kullanimi = Column(Float)
    disk_kullanimi = Column(Float)
    aktif_baglanti_sayisi = Column(Integer)
    detaylar = Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'zaman': self.zaman.isoformat(),
            'cpu_kullanimi': self.cpu_kullanimi,
            'ram_kullanimi': self.ram_kullanimi,
            'disk_kullanimi': self.disk_kullanimi,
            'aktif_baglanti_sayisi': self.aktif_baglanti_sayisi,
            'detaylar': self.detaylar
        }

class VeritabaniYoneticisi:
    """Veritabanı işlemlerini yöneten sınıf."""
    
    def __init__(self, db_url: str = None):
        """
        Args:
            db_url: Veritabanı bağlantı URL'si. None ise SQLite kullanılır.
        """
        if db_url is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'threattracker.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db_url = f'sqlite:///{db_path}'
        
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Veritabanı tablolarını oluşturur."""
        Base.metadata.create_all(self.engine)
    
    def kaydet_tehdit(self, tip: TehditTipi, kaynak_ip: str = None, 
                      hedef_ip: str = None, detaylar: dict = None,
                      onem_derecesi: int = 1) -> Tehdit:
        """Yeni bir tehdit kaydı oluşturur.
        
        Args:
            tip: Tehdit tipi
            kaynak_ip: Tehdidin kaynağı olan IP
            hedef_ip: Hedef IP adresi
            detaylar: Tehdit ile ilgili ek bilgiler
            onem_derecesi: Tehdidin önem derecesi (1-5)
            
        Returns:
            Tehdit: Oluşturulan tehdit kaydı
        """
        session = self.Session()
        try:
            tehdit = Tehdit(
                tip=tip,
                kaynak_ip=kaynak_ip,
                hedef_ip=hedef_ip,
                detaylar=detaylar,
                onem_derecesi=onem_derecesi
            )
            session.add(tehdit)
            session.commit()
            return tehdit
        finally:
            session.close()
    
    def kaydet_olay(self, tip: str, kaynak: str, mesaj: str,
                    tehdit_id: int = None, detaylar: dict = None) -> Olay:
        """Yeni bir olay kaydı oluşturur.
        
        Args:
            tip: Olay tipi
            kaynak: Olayın kaynağı
            mesaj: Olay mesajı
            tehdit_id: İlişkili tehdit ID'si
            detaylar: Olay ile ilgili ek bilgiler
            
        Returns:
            Olay: Oluşturulan olay kaydı
        """
        session = self.Session()
        try:
            olay = Olay(
                tip=tip,
                kaynak=kaynak,
                mesaj=mesaj,
                tehdit_id=tehdit_id,
                detaylar=detaylar
            )
            session.add(olay)
            session.commit()
            return olay
        finally:
            session.close()
    
    def kaydet_sistem_durumu(self, cpu_kullanimi: float, ram_kullanimi: float,
                            disk_kullanimi: float, aktif_baglanti_sayisi: int,
                            detaylar: dict = None) -> SistemDurumu:
        """Yeni bir sistem durumu kaydı oluşturur."""
        session = self.Session()
        try:
            durum = SistemDurumu(
                cpu_kullanimi=cpu_kullanimi,
                ram_kullanimi=ram_kullanimi,
                disk_kullanimi=disk_kullanimi,
                aktif_baglanti_sayisi=aktif_baglanti_sayisi,
                detaylar=detaylar
            )
            session.add(durum)
            session.commit()
            return durum
        finally:
            session.close() 