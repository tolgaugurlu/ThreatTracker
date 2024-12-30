# ThreatTracker

ThreatTracker, sistem ve ağ güvenliğini izlemek için geliştirilmiş bir güvenlik aracıdır. Makine öğrenimi tabanlı anomali tespiti, ağ taraması ve tehdit analizi gibi özellikleri içerir.

## Özellikler

- Sistem kaynaklarının (CPU, RAM, disk) gerçek zamanlı izlenmesi
- Ağ trafiği analizi ve port taraması
- Makine öğrenimi tabanlı anomali tespiti
- Tehdit tespiti ve uyarı sistemi
- Kullanıcı dostu grafiksel arayüz

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/tolgaugurlu/ThreatTracker.git
cd ThreatTracker
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
.\venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

Uygulamayı başlatmak için:
```bash
python src/main.py
```

## Testler

Testleri çalıştırmak için:
```bash
pytest tests/
```

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin yeni-ozellik`)
5. Pull request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Geliştirici

- **Tolga Uğurlu**
  - GitHub: [@tolgaugurlu](https://github.com/tolgaugurlu)
  - LinkedIn: [Tolga Uğurlu](https://www.linkedin.com/in/tolgaugurlu/)

## Güvenlik

Bu aracı yalnızca yetkili olduğunuz sistemlerde ve ağlarda kullanın. Yetkisiz kullanım yasal sonuçlar doğurabilir. 