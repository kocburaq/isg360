import { type ModuleId } from '@/types/factory'
import { Cctv, type LucideIcon } from 'lucide-react'

export type ModuleStatus = 'active' | 'coming-soon'

export type ModuleDefinition = {
  id: ModuleId
  title: string
  description: string
  icon: LucideIcon
  /** Uygulama içi rota. */
  url: '/cameras'
  status: ModuleStatus
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
    description: 'Kamera görüntüleri, görüntü işleme ve KKD denetimi',
    icon: Cctv,
    url: '/cameras',
    status: 'active',
  },
]

export function getModule(id: ModuleId): ModuleDefinition {
  const found = modules.find((m) => m.id === id)
  if (!found) throw new Error(`Bilinmeyen modül: ${id}`)
  return found
}
