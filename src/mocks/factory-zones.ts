import { type FactoryZone } from '@/types/factory'

/** ÖRNEK VERİ — gerçek tesis yerleşimi değildir. */
export const mockZones = {
  entrance: { id: 'zone-entrance', name: 'Giriş ve Güvenlik', area: 'A Blok' },
  assembly: { id: 'zone-assembly', name: 'Montaj Holü', area: 'B Blok' },
  production: {
    id: 'zone-production',
    name: 'Üretim Atölyesi',
    area: 'B Blok',
  },
  logistics: { id: 'zone-logistics', name: 'Lojistik ve Depo', area: 'C Blok' },
  hazmat: {
    id: 'zone-hazmat',
    name: 'Tehlikeli Madde Alanı',
    area: 'D Blok',
  },
} satisfies Record<string, FactoryZone>
