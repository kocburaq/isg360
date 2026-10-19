import { ModuleComingSoon } from '@/components/module-coming-soon'

/**
 * Drone Yönetimi modülü.
 * Geliştirildiğinde kamera modülüyle aynı katman yapısını izleyecek:
 * api/ (servis arayüzü + mock/http), hooks/, components/, types.ts
 */
export function Drones() {
  return <ModuleComingSoon moduleId='drones' />
}
