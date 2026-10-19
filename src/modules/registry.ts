import { type ModuleId } from '@/types/factory'
import { ClipboardList, Cctv, Plane, type LucideIcon } from 'lucide-react'

export type ModuleStatus = 'active' | 'coming-soon'

export type ModuleDefinition = {
  id: ModuleId
  title: string
  description: string
  icon: LucideIcon
  /** Uygulama içi rota. */
  url: '/cameras' | '/work-orders' | '/drones'
  status: ModuleStatus
  /** "Yakında" sayfasında gösterilen planlanan yetenekler. */
  plannedFeatures: string[]
}

/**
 * Uygulamadaki tüm modüllerin tek kaynağı.
 * Ana panel kartları, sidebar ve komut menüsü bu listeden beslenir;
 * yeni bir modül eklemek için önce buraya kayıt eklenir.
 */
export const modules: ModuleDefinition[] = [
  {
    id: 'cameras',
    title: 'Kamera Yönetimi',
    description: 'Kamera görüntüleri ve KKD denetimi',
    icon: Cctv,
    url: '/cameras',
    status: 'active',
    plannedFeatures: [
      'RTSP IP kamera bağlantıları',
      'YOLO tabanlı KKD tespiti',
      'İhlal bildirimleri ve raporlama',
    ],
  },
  {
    id: 'work-orders',
    title: 'İş Kartları',
    description: 'Fabrikadaki görev ve iş süreçleri',
    icon: ClipboardList,
    url: '/work-orders',
    status: 'coming-soon',
    plannedFeatures: [
      'İş kartı oluşturma, atama ve takip',
      'Bölge ve ekipman bazlı görev planlama',
      'KKD ihlallerinden otomatik düzeltici faaliyet kartı',
      'Onay akışları ve iş geçmişi',
    ],
  },
  {
    id: 'drones',
    title: 'Drone Yönetimi',
    description: 'Drone kontrolü ve görev planlama',
    icon: Plane,
    url: '/drones',
    status: 'coming-soon',
    plannedFeatures: [
      'Drone filosu durum takibi',
      'Rota ve devriye görevi planlama',
      'Tesis içi alan denetimi ve görüntü aktarımı',
      'Kamera modülüyle ortak olay kayıtları',
    ],
  },
]

export function getModule(id: ModuleId): ModuleDefinition {
  const found = modules.find((m) => m.id === id)
  if (!found) throw new Error(`Bilinmeyen modül: ${id}`)
  return found
}
