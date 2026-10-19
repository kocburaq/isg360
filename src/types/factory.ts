import { type EntityId } from './common'

/**
 * Modüller arası paylaşılan fabrika alan modeli.
 * Kamera, İş Kartları ve Drone modülleri aynı bölge (zone) kavramını kullanır;
 * böylece örneğin bir KKD ihlali ilgili bölgedeki iş kartına bağlanabilir.
 */

export type ModuleId = 'cameras' | 'work-orders' | 'drones'

export type FactoryZone = {
  id: EntityId
  name: string
  /** Bina / hol / hat gibi üst konum bilgisi. */
  area: string
}

/**
 * Başka bir modüldeki kayda referans.
 * İleride ihlal → iş kartı, drone görevi → kamera gibi bağlantılar için kullanılır.
 */
export type EntityRef = {
  module: ModuleId
  id: EntityId
}
