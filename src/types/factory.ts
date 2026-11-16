import { type EntityId } from './common'

/**
 * Fabrika alan modeli: fabrika → bölgeler → kameralar.
 */

export type ModuleId = 'cameras'

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
