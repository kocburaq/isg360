import { useSearch } from '@tanstack/react-router'
import { AuthLayout } from '../auth-layout'
import { UserAuthForm } from './components/user-auth-form'

export function SignIn() {
  const { redirect } = useSearch({ from: '/(auth)/sign-in' })

  return (
    <AuthLayout>
      <div className='space-y-1.5'>
        <h1 className='text-2xl font-semibold tracking-tight'>
          Yönetici Girişi
        </h1>
        <p className='text-sm text-muted-foreground'>
          Devam etmek için kullanıcı adınızı ve şifrenizi girin.
        </p>
      </div>
      <UserAuthForm redirectTo={redirect} />
    </AuthLayout>
  )
}
