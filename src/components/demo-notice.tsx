import { env } from '@/config/env'
import { FlaskConical } from 'lucide-react'
import { useCurrentUser } from '@/hooks/use-current-user'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

/**
 * Prototip uyarısı: demo oturumu, örnek veri veya kimlik doğrulamasız API
 * kullanıldığında gösterilir. Kullanıcının simüle edilmiş içeriği gerçek sanmasını engeller.
 */
export function DemoNotice() {
  const { isDemo } = useCurrentUser()
  const usingApi = env.dataSource === 'api'

  return (
    <Alert className='border-warning/40 bg-warning/5'>
      <FlaskConical className='text-warning' />
      <AlertTitle>Prototip / Demo Modu</AlertTitle>
      <AlertDescription>
        {isDemo &&
          'Demo oturumu açıktır; gerçek kimlik doğrulama ve güvenlik yoktur. '}
        {usingApi
          ? 'Veriler yerel FastAPI backend’inden gelir ve veritabanında kalıcıdır. Kamera ve ihlal kayıtları örnek (simüle) verilerdir; gerçek kamera veya yapay zekâ modeline bağlı değildir. API’de henüz kimlik doğrulama yoktur.'
          : 'Gösterilen kamera, tespit ve ihlal verileri örnek (simüle) verilerdir; gerçek kamera veya yapay zekâ modeline bağlı değildir.'}
      </AlertDescription>
    </Alert>
  )
}
