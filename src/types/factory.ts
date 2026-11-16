import { type EntityId } from './common'

/**
 * Modüller arası paylaşılan fabrika alan modeli.
 * Kamera, İş Kartları ve Drone modülleri aynı bölge (zone) kavramını kullanır;
 * böylece örneğin bir KKD ihlali ilgili bölgedeki iş kartına bağlanabilir.
 */

export type ModuleId = 'cameras' | 'work-orders' | 'drones'

/** Fabrika (backend: GET /factories). */
export type Factory = {
  id: EntityId
  /** Kısa kod, ör. "F01". */
  code: string
  name: string
  city?: string | null
  timezone?: string
}

/** Kayıtlarda taşınan kısa fabrika bilgisi. */
export type FactoryRef = Pick<Factory, 'id' | 'code' | 'name'>

export type FactoryZone = {
  id: EntityId
  /** Bölgenin bağlı olduğu fabrika. */
  factoryId: EntityId
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
