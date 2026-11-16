import { Anchor, Ban, ShieldAlert, type LucideIcon } from 'lucide-react'
import { type PpeViolation, type ViolationType } from '../types'
import { getPpeClass } from './ppe-classes'

export type ViolationTypeDefinition = {
  id: ViolationType
  label: string
  icon: LucideIcon
}

/** İhlal türleri (backend ve edge sözleşmesiyle aynı kimlikler). */
export const VIOLATION_TYPES: Record<ViolationType, ViolationTypeDefinition> = {
  missing_ppe: { id: 'missing_ppe', label: 'Eksik KKD', icon: ShieldAlert },
  restricted_area: {
    id: 'restricted_area',
    label: 'Yasaklı bölgeye giriş',
    icon: Ban,
  },
  missing_harness: {
    id: 'missing_harness',
    label: 'Yüksekte emniyet kemeri yok',
    icon: Anchor,
  },
}

export type ViolationLabelPart = {
  key: string
  label: string
  icon: LucideIcon
}

/**
 * İhlalin kısa açıklaması. KKD ihlallerinde her eksik sınıf ayrı gösterilir
 * ("Baret yok", "Reflektörlü Yelek yok"); diğer türlerde tür etiketi kullanılır.
 */
export function violationLabelParts(
  violation: Pick<PpeViolation, 'violationType' | 'missing'>
): ViolationLabelPart[] {
  // Eski kayıtlarda violationType olmayabilir: KKD ihlali varsayılır
  const type = violation.violationType ?? 'missing_ppe'
  if (type === 'missing_ppe' && violation.missing.length > 0) {
    return violation.missing.map((id) => {
      const ppe = getPpeClass(id)
      return { key: id, label: `${ppe.label} yok`, icon: ppe.icon }
    })
  }
  const def = VIOLATION_TYPES[type]
  return [{ key: def.id, label: def.label, icon: def.icon }]
}
