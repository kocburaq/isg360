import { modules } from '@/modules/registry'
import { LayoutDashboard } from 'lucide-react'
import { type NavGroup } from '../types'

/**
 * Sidebar gezinme grupları. Modül bağlantıları modül kaydından üretilir;
 * böylece yeni bir modül eklendiğinde menü otomatik güncellenir.
 */
export const navGroups: NavGroup[] = [
  {
    title: 'Genel',
    items: [
      {
        title: 'Ana Kontrol Paneli',
        url: '/',
        icon: LayoutDashboard,
      },
    ],
  },
  {
    title: 'Modüller',
    items: modules.map((m) => ({
      title: m.title,
      url: m.url,
      icon: m.icon,
      badge: m.status === 'coming-soon' ? 'Yakında' : undefined,
    })),
  },
]
