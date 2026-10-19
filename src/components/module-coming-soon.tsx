import { Link } from '@tanstack/react-router'
import { getModule } from '@/modules/registry'
import { type ModuleId } from '@/types/factory'
import { ArrowLeft, CircleDashed } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { AppHeader } from '@/components/layout/app-header'
import { Main } from '@/components/layout/main'

type ModuleComingSoonProps = {
  moduleId: ModuleId
}

/** Henüz geliştirilmemiş modüller için ortak "Yakında" sayfası. */
export function ModuleComingSoon({ moduleId }: ModuleComingSoonProps) {
  const module = getModule(moduleId)
  const Icon = module.icon

  return (
    <>
      <AppHeader />
      <Main className='flex flex-1 items-center justify-center'>
        <Card className='w-full max-w-xl'>
          <CardHeader className='items-start gap-4'>
            <div className='flex w-full items-center justify-between'>
              <div className='flex size-14 items-center justify-center rounded-lg bg-muted text-muted-foreground'>
                <Icon className='size-7' />
              </div>
              <Badge variant='secondary'>Yakında</Badge>
            </div>
            <div className='space-y-1.5'>
              <CardTitle className='text-2xl'>{module.title}</CardTitle>
              <CardDescription>
                {module.description}. Bu modül geliştirme aşamasındadır ve
                sonraki sürümlerde kullanıma açılacaktır.
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className='space-y-6'>
            <div className='space-y-3'>
              <h2 className='text-sm font-medium text-muted-foreground'>
                Planlanan özellikler
              </h2>
              <ul className='space-y-2'>
                {module.plannedFeatures.map((feature) => (
                  <li key={feature} className='flex items-start gap-2 text-sm'>
                    <CircleDashed className='mt-0.5 size-4 shrink-0 text-muted-foreground' />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
            <Button variant='outline' asChild>
              <Link to='/'>
                <ArrowLeft className='rtl:rotate-180' />
                Ana panele dön
              </Link>
            </Button>
          </CardContent>
        </Card>
      </Main>
    </>
  )
}
