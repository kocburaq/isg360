import { APP_CONFIG } from '@/config/app'
import { Logo } from '@/assets/logo'
import { ThemeSwitch } from '@/components/theme-switch'

type AuthLayoutProps = {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className='relative grid min-h-svh lg:grid-cols-2'>
      <div className='absolute end-4 top-4 z-10'>
        <ThemeSwitch />
      </div>

      {/* Kurumsal bilgi paneli (yalnızca geniş ekranlarda) */}
      <aside className='relative hidden flex-col justify-between overflow-hidden border-e bg-sidebar p-10 lg:flex'>
        <div
          aria-hidden='true'
          className='pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-size-[48px_48px] opacity-60'
        />
        <div className='relative flex items-center gap-3'>
          <div className='flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground'>
            <Logo className='size-5' />
          </div>
          <div className='leading-tight'>
            <p className='font-semibold'>{APP_CONFIG.name}</p>
            <p className='text-sm text-muted-foreground'>
              {APP_CONFIG.tagline}
            </p>
          </div>
        </div>
        <div className='relative max-w-md space-y-3'>
          <h2 className='text-3xl font-semibold tracking-tight'>
            Tesis güvenliği ve operasyonlar tek merkezde.
          </h2>
          <p className='text-muted-foreground'>
            Kamera ve KKD denetimi, iş kartları ve drone görevleri için modüler
            yönetim paneli.
          </p>
        </div>
        <p className='relative text-xs text-muted-foreground'>
          Sürüm {APP_CONFIG.version} · Prototip
        </p>
      </aside>

      <main className='flex items-center justify-center px-4 py-12 sm:px-8'>
        <div className='w-full max-w-sm space-y-6'>
          <div className='flex items-center justify-center gap-2 lg:hidden'>
            <Logo />
            <h1 className='text-lg font-semibold'>{APP_CONFIG.name}</h1>
          </div>
          {children}
        </div>
      </main>
    </div>
  )
}
