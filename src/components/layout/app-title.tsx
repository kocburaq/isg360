import { Link } from '@tanstack/react-router'
import { APP_CONFIG } from '@/config/app'
import { Logo } from '@/assets/logo'
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar'

export function AppTitle() {
  const { setOpenMobile } = useSidebar()
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size='lg' asChild tooltip={APP_CONFIG.name}>
          <Link to='/' onClick={() => setOpenMobile(false)}>
            <div className='flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground'>
              <Logo className='size-4' />
            </div>
            <div className='grid flex-1 text-start text-sm leading-tight'>
              <span className='truncate font-semibold'>{APP_CONFIG.name}</span>
              <span className='truncate text-xs text-muted-foreground'>
                {APP_CONFIG.tagline}
              </span>
            </div>
          </Link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
