import { type Camera } from '@/features/cameras/types'
import { mockZones } from './factory-zones'
import { minutesAgo } from './utils'

const defaultStream = {
  protocol: 'rtsp',
  configured: false,
  resolution: '1920×1080',
  fps: 25,
} as const

/** ÖRNEK VERİ — gerçek kamera bağlantısı yoktur. */
export function createMockCameras(): Camera[] {
  return [
    {
      id: 'cam-01',
      code: 'CAM-01',
      name: 'Ana Giriş Kapısı',
      zone: mockZones.entrance,
      location: 'Personel turnikeleri, kuzey cephe',
      status: 'online',
      lastSeenAt: minutesAgo(0),
      stream: { ...defaultStream },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
    {
      id: 'cam-02',
      code: 'CAM-02',
      name: 'Montaj Hattı 1',
      zone: mockZones.assembly,
      location: 'Hat başı, istasyon 1–4',
      status: 'online',
      lastSeenAt: minutesAgo(0),
      stream: { ...defaultStream },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
    {
      id: 'cam-03',
      code: 'CAM-03',
      name: 'Kaynak Atölyesi',
      zone: mockZones.production,
      location: 'Kaynak kabinleri önü',
      status: 'online',
      lastSeenAt: minutesAgo(1),
      stream: { ...defaultStream, resolution: '2560×1440' },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
    {
      id: 'cam-04',
      code: 'CAM-04',
      name: 'Depo ve Sevkiyat',
      zone: mockZones.logistics,
      location: 'Yükleme rampası 2',
      status: 'online',
      lastSeenAt: minutesAgo(0),
      stream: { ...defaultStream },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
    {
      id: 'cam-05',
      code: 'CAM-05',
      name: 'Forklift Koridoru',
      zone: mockZones.logistics,
      location: 'Raf blokları arası ana koridor',
      status: 'offline',
      lastSeenAt: minutesAgo(134),
      stream: { ...defaultStream, fps: 15, resolution: '1280×720' },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
    {
      id: 'cam-06',
      code: 'CAM-06',
      name: 'Kimyasal Depolama',
      zone: mockZones.hazmat,
      location: 'Depo kapısı iç taraf',
      status: 'online',
      lastSeenAt: minutesAgo(2),
      stream: { ...defaultStream },
      ppeClasses: ['helmet', 'vest'],
      isSimulated: true,
    },
  ]
}
