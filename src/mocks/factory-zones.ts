import { type Factory, type FactoryZone } from '@/types/factory'

/** ÖRNEK VERİ — backend seed (backend/app/db/seed.py) ile aynıdır. */
export const mockFactories = {
  main: {
    id: 'fac-default',
    code: 'F01',
    name: 'Merkez Fabrika',
    city: 'İstanbul',
    timezone: 'Europe/Istanbul',
  },
  gebze: {
    id: 'fac-gebze',
    code: 'F02',
    name: 'Gebze Fabrikası',
    city: 'Kocaeli',
    timezone: 'Europe/Istanbul',
  },
} satisfies Record<string, Factory>

/** ÖRNEK VERİ — gerçek tesis yerleşimi değildir. */
export const mockZones = {
  entrance: {
    id: 'zone-entrance',
    factoryId: 'fac-default',
    name: 'Giriş ve Güvenlik',
    area: 'A Blok',
  },
  assembly: {
    id: 'zone-assembly',
    factoryId: 'fac-default',
    name: 'Montaj Holü',
    area: 'B Blok',
  },
  production: {
    id: 'zone-production',
    factoryId: 'fac-default',
    name: 'Üretim Atölyesi',
    area: 'B Blok',
  },
  logistics: {
    id: 'zone-logistics',
    factoryId: 'fac-default',
    name: 'Lojistik ve Depo',
    area: 'C Blok',
  },
  hazmat: {
    id: 'zone-hazmat',
    factoryId: 'fac-default',
    name: 'Tehlikeli Madde Alanı',
    area: 'D Blok',
  },
  press: {
    id: 'zone-press',
    factoryId: 'fac-gebze',
    name: 'Pres Hattı',
    area: 'P1 Hol',
  },
} satisfies Record<string, FactoryZone>

/** Bölge kimliğinden fabrika kimliğine. */
export function factoryIdOfZone(zoneId: string): string {
  const zone = Object.values(mockZones).find((z) => z.id === zoneId)
  return zone?.factoryId ?? mockFactories.main.id
}
