import {
  Footprints,
  Glasses,
  Hand,
  HardHat,
  Shirt,
  type LucideIcon,
} from 'lucide-react'
import { type PpeClassId } from '../types'

export type PpeClassDefinition = {
  id: PpeClassId
  label: string
  shortLabel: string
  icon: LucideIcon
  /** false: arayüzde "planlanıyor" olarak gösterilir, denetimde kullanılmaz. */
  enabled: boolean
  /**
   * YOLO modelindeki sınıf etiketleri (eğitim veri setine göre güncellenecek).
   * Backend, model çıktısını bu kimliklere eşleyerek gönderir.
   */
  modelLabels: { present: string; absent: string }
}

export const PPE_CLASSES: PpeClassDefinition[] = [
  {
    id: 'helmet',
    label: 'Baret',
    shortLabel: 'Baret',
    icon: HardHat,
    enabled: true,
    modelLabels: { present: 'helmet', absent: 'no_helmet' },
  },
  {
    id: 'vest',
    label: 'Reflektörlü Yelek',
    shortLabel: 'Yelek',
    icon: Shirt,
    enabled: true,
    modelLabels: { present: 'vest', absent: 'no_vest' },
  },
  {
    id: 'gloves',
    label: 'İş Eldiveni',
    shortLabel: 'Eldiven',
    icon: Hand,
    enabled: false,
    modelLabels: { present: 'gloves', absent: 'no_gloves' },
  },
  {
    id: 'goggles',
    label: 'Koruyucu Gözlük',
    shortLabel: 'Gözlük',
    icon: Glasses,
    enabled: false,
    modelLabels: { present: 'goggles', absent: 'no_goggles' },
  },
  {
    id: 'safety-boots',
    label: 'İş Ayakkabısı',
    shortLabel: 'Ayakkabı',
    icon: Footprints,
    enabled: false,
    modelLabels: { present: 'boots', absent: 'no_boots' },
  },
]

const byId = new Map(PPE_CLASSES.map((c) => [c.id, c]))

export function getPpeClass(id: PpeClassId): PpeClassDefinition {
  return byId.get(id)!
}

export const ENABLED_PPE_CLASSES = PPE_CLASSES.filter((c) => c.enabled)
export const PLANNED_PPE_CLASSES = PPE_CLASSES.filter((c) => !c.enabled)
