import { ConfigDrawer } from '@/components/config-drawer'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Header } from './header'

type AppHeaderProps = {
  /** Arama alanının solunda gösterilecek ek içerik (ör. sayfa başlığı). */
  children?: React.ReactNode
  fixed?: boolean
}

/** Oturum açılmış tüm sayfalarda kullanılan standart üst bar. */
export function AppHeader({ children, fixed }: AppHeaderProps) {
  return (
    <Header fixed={fixed}>
      {children}
      <Search className='me-auto' />
      <ThemeSwitch />
      <ConfigDrawer />
      <ProfileDropdown />
    </Header>
  )
}
