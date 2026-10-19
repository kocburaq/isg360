import { env } from '@/config/env'
import { FlaskConical } from 'lucide-react'
import { useCurrentUser } from '@/hooks/use-current-user'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

/**
 * Prototip uyarısı: demo oturumu veya örnek veri kullanıldığında gösterilir.
 * Kullanıcının simüle edilmiş içeriği gerçek sanmasını engeller.
 */
export function DemoNotice() {
  const { isDemo } = useCurrentUser()
  const usingMockData = env.dataSource === 'mock'

  if (!isDemo && !usingMockData) return null

  return (
    <Alert className='border-warning/40 bg-warning/5'>
      <FlaskConical className='text-warning' />
      <AlertTitle>Prototip / Demo Modu</AlertTitle>
      <AlertDescription>
        {isDemo &&
          'Demo oturumu açıktır; gerçek kimlik doğrulama ve güvenlik yoktur. '}
        {usingMockData &&
          'Gösterilen kamera, tespit ve ihlal verileri örnek (simüle) verilerdir; gerçek kamera veya yapay zekâ modeline bağlı değildir.'}
      </AlertDescription>
    </Alert>
  )
}
