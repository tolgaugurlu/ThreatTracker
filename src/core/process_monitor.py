#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
from datetime import datetime
from loguru import logger
from typing import Dict, List, Optional

class ProcessMonitor:
    """Sistem süreçlerini izleyen ve analiz eden sınıf."""
    
    def __init__(self):
        """ProcessMonitor sınıfının başlatıcısı."""
        self.previous_processes: Dict[int, Dict] = {}
        logger.info("ProcessMonitor başlatıldı")
    
    def get_process_info(self, process: psutil.Process) -> Dict:
        """Belirli bir sürecin detaylı bilgilerini alır.
        
        Args:
            process: psutil.Process nesnesi
            
        Returns:
            Dict: Süreç bilgilerini içeren sözlük
        """
        try:
            with process.oneshot():
                return {
                    'pid': process.pid,
                    'name': process.name(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent(),
                    'status': process.status(),
                    'create_time': datetime.fromtimestamp(process.create_time()),
                    'username': process.username(),
                    'cmdline': ' '.join(process.cmdline()) if process.cmdline() else '',
                    'connections': len(process.connections()),
                    'open_files': len(process.open_files())
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return {}
    
    def get_all_processes(self) -> List[Dict]:
        """Sistemdeki tüm süreçlerin bilgilerini toplar.
        
        Returns:
            List[Dict]: Süreç bilgilerini içeren sözlük listesi
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = self.get_process_info(proc)
                if proc_info:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes
    
    def detect_new_processes(self) -> List[Dict]:
        """Yeni başlatılan süreçleri tespit eder.
        
        Returns:
            List[Dict]: Yeni süreç bilgilerini içeren sözlük listesi
        """
        current_processes = {p['pid']: p for p in self.get_all_processes()}
        new_processes = []
        
        for pid, proc_info in current_processes.items():
            if pid not in self.previous_processes:
                new_processes.append(proc_info)
                logger.info(f"Yeni süreç tespit edildi: {proc_info['name']} (PID: {pid})")
        
        self.previous_processes = current_processes
        return new_processes
    
    def detect_suspicious_processes(self, cpu_threshold: float = 80.0, 
                                 memory_threshold: float = 80.0) -> List[Dict]:
        """Şüpheli süreçleri tespit eder.
        
        Args:
            cpu_threshold: CPU kullanım eşiği (yüzde)
            memory_threshold: Bellek kullanım eşiği (yüzde)
            
        Returns:
            List[Dict]: Şüpheli süreç bilgilerini içeren sözlük listesi
        """
        suspicious = []
        for process in self.get_all_processes():
            if (process.get('cpu_percent', 0) > cpu_threshold or 
                process.get('memory_percent', 0) > memory_threshold):
                suspicious.append(process)
                logger.warning(f"Şüpheli süreç tespit edildi: {process['name']} "
                             f"(PID: {process['pid']}, CPU: {process['cpu_percent']}%, "
                             f"Memory: {process['memory_percent']}%)")
        return suspicious

if __name__ == "__main__":
    # Test kodu
    monitor = ProcessMonitor()
    print("Aktif süreçler:")
    for proc in monitor.get_all_processes():
        print(f"PID: {proc['pid']}, Name: {proc['name']}, "
              f"CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']}%") 