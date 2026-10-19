import { format, formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'

/** "5 dakika önce" */
export function formatRelative(iso: string): string {
  return formatDistanceToNow(new Date(iso), { addSuffix: true, locale: tr })
}

/** "18.10.2026 14:32" */
export function formatDateTime(iso: string): string {
  return format(new Date(iso), 'dd.MM.yyyy HH:mm', { locale: tr })
}

/** "14:32:05" */
export function formatTime(iso: string): string {
  return format(new Date(iso), 'HH:mm:ss', { locale: tr })
}

/** 0.913 → "%91" */
export function formatPercent(ratio: number): string {
  return `%${Math.round(ratio * 100)}`
}
