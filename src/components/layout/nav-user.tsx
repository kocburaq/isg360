import { ChevronsUpDown, FlaskConical, LogOut } from 'lucide-react'
import { useCurrentUser } from '@/hooks/use-current-user'
import useDialogState from '@/hooks/use-dialog-state'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar'
import { SignOutDialog } from '@/components/sign-out-dialog'

export function NavUser() {
  const { isMobile } = useSidebar()
  const [open, setOpen] = useDialogState()
  const { user, initials, isDemo, roleLabel } = useCurrentUser()

  if (!user) return null

  return (
    <>
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SidebarMenuButton
                size='lg'
                className='data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground'
              >
                <Avatar className='h-8 w-8 rounded-lg'>
                  <AvatarFallback className='rounded-lg'>
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className='grid flex-1 text-start text-sm leading-tight'>
                  <span className='truncate font-semibold'>
                    {user.displayName}
                  </span>
                  <span className='truncate text-xs'>
                    {roleLabel}
                    {isDemo && ' · Demo'}
                  </span>
                </div>
                <ChevronsUpDown className='ms-auto size-4' />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className='w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg'
              side={isMobile ? 'bottom' : 'right'}
              align='end'
              sideOffset={4}
            >
              <DropdownMenuLabel className='p-0 font-normal'>
                <div className='grid px-1 py-1.5 text-start text-sm leading-tight'>
                  <span className='truncate font-semibold'>
                    {user.displayName}
                  </span>
                  <span className='truncate text-xs text-muted-foreground'>
                    @{user.username}
                  </span>
                </div>
              </DropdownMenuLabel>
              {isDemo && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className='flex items-center gap-2 text-xs font-normal text-amber-600 dark:text-amber-400'>
                    <FlaskConical className='size-3.5' />
                    Demo oturumu — güvenlik sağlamaz
                  </DropdownMenuLabel>
                </>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                variant='destructive'
                onClick={() => setOpen(true)}
              >
                <LogOut />
                Çıkış Yap
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>

      <SignOutDialog open={!!open} onOpenChange={setOpen} />
    </>
  )
}
