import {
  type CameraStatus,
  type PpeCheckState,
  type ServiceState,
  type ViolationSeverity,
  type ViolationStatus,
} from '../types'

/** Durum değerlerinin Türkçe etiketleri ve görsel sınıfları (tek kaynak). */

type StatusMeta = { label: string; className: string }

export const CAMERA_STATUS: Record<CameraStatus, StatusMeta> = {
  online: {
    label: 'Çevrimiçi',
    className: 'border-success/30 bg-success/15 text-success',
  },
  offline: {
    label: 'Çevrimdışı',
    className: 'border-destructive/30 bg-destructive/15 text-destructive',
  },
  unknown: {
    label: 'Bilinmiyor',
    className: 'border-border bg-muted text-muted-foreground',
  },
}

export const CHECK_STATE: Record<PpeCheckState, StatusMeta> = {
  compliant: { label: 'Uyumlu', className: 'text-success' },
  violation: { label: 'İhlal', className: 'text-destructive' },
  unknown: { label: 'Belirsiz', className: 'text-muted-foreground' },
}

export const VIOLATION_STATUS: Record<ViolationStatus, StatusMeta> = {
  open: {
    label: 'Açık',
    className: 'border-destructive/30 bg-destructive/15 text-destructive',
  },
  acknowledged: {
    label: 'İncelendi',
    className: 'border-warning/30 bg-warning/15 text-warning',
  },
  resolved: {
    label: 'Çözüldü',
    className: 'border-success/30 bg-success/15 text-success',
  },
}

export const VIOLATION_SEVERITY: Record<ViolationSeverity, StatusMeta> = {
  low: { label: 'Düşük', className: 'text-muted-foreground' },
  medium: { label: 'Orta', className: 'text-warning' },
  high: { label: 'Yüksek', className: 'text-destructive' },
}

export const SERVICE_STATE: Record<ServiceState, StatusMeta> = {
  operational: { label: 'Çalışıyor', className: 'text-success' },
  degraded: { label: 'Kısıtlı', className: 'text-warning' },
  down: { label: 'Erişilemiyor', className: 'text-destructive' },
  simulated: { label: 'Simülasyon', className: 'text-warning' },
}
