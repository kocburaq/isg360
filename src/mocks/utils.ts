/** Mock veri katmanı yardımcıları. */

/** Şu andan `minutes` dakika önceki zamanın ISO karşılığı. */
export function minutesAgo(minutes: number): string {
  return new Date(Date.now() - minutes * 60_000).toISOString()
}

/** Ağ gecikmesini taklit eder; yükleme durumlarının arayüzde görülmesini sağlar. */
export function simulateLatency(ms = 300): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/** Mock kayıtların dışarıdan değiştirilmesini önlemek için derin kopya. */
export function clone<T>(value: T): T {
  return structuredClone(value)
}
