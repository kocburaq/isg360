import { modules } from '@/modules/registry'
import { useCurrentUser } from '@/hooks/use-current-user'
import { DemoNotice } from '@/components/demo-notice'
import { AppHeader } from '@/components/layout/app-header'
import { Main } from '@/components/layout/main'
import { PageHeading } from '@/components/page-heading'
import { ModuleCard } from './components/module-card'

export function Dashboard() {
  const { user } = useCurrentUser()

  return (
    <>
      <AppHeader />

      <Main className='space-y-6'>
        <PageHeading
          title='Ana Kontrol Paneli'
          description={
            user
              ? `Hoş geldiniz, ${user.displayName}. Çalışmak istediğiniz modülü seçin.`
              : 'Çalışmak istediğiniz modülü seçin.'
          }
        />

        <DemoNotice />

        <section aria-label='Modüller' className='grid gap-4 md:grid-cols-3'>
          {modules.map((module) => (
            <ModuleCard key={module.id} module={module} />
          ))}
        </section>
      </Main>
    </>
  )
}
