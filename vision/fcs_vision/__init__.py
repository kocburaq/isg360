"""Factory Control System — saha (edge) görüntü işleme servisi.

Planlanan alt paketler (bkz. README):
    sync/       merkez ile iletişim: yapılandırma, heartbeat, olay kuyruğu (3.1) ✔
    simulator/  gerçek kamera/model olmadan sahte olay üreten simülatör (3.1) ✔
    rules/      kural motoru (3.2)
    ingest/     RTSP / video dosyası okuma (3.3)
    inference/  dedektör eklentileri, ONNX çalışma ortamı (3.4)
    tracking/   kişi takibi (3.4)
    evidence/   kanıt görüntüsü, bulanıklaştırma, yükleme (3.6)
"""

__version__ = "0.1.0"
