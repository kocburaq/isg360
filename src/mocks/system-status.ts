import { type SystemStatus } from '@/features/cameras/types'

/**
 * Prototipte gerçek servis olmadığı için tüm bileşenler dürüstçe
 * "simülasyon" olarak raporlanır.
 */
export function createMockSystemStatus(): SystemStatus {
  return {
    state: 'simulated',
    checkedAt: new Date().toISOString(),
    services: [
      {
        id: 'inference',
        label: 'Görüntü işleme (YOLO)',
        state: 'simulated',
        detail: 'Model bağlı değil; tespitler simüle ediliyor.',
      },
      {
        id: 'stream-gateway',
        label: 'Kamera akış ağ geçidi (RTSP)',
        state: 'simulated',
        detail: 'Gerçek kamera bağlantısı yapılandırılmadı.',
      },
      {
        id: 'api',
        label: 'Backend API (FastAPI)',
        state: 'simulated',
        detail: 'Örnek veri katmanı kullanılıyor.',
      },
    ],
  }
}
