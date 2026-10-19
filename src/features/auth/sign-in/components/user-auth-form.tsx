import { useState } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from '@tanstack/react-router'
import { authService } from '@/services/auth/auth-service'
import { AuthUnavailableError, type AuthSession } from '@/services/auth/types'
import { FlaskConical, Loader2, LogIn, TriangleAlert } from 'lucide-react'
import { toast } from 'sonner'
import { useAuthStore } from '@/stores/auth-store'
import { safeRedirectPath } from '@/lib/safe-redirect'
import { cn } from '@/lib/utils'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { PasswordInput } from '@/components/password-input'

const formSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, 'Lütfen kullanıcı adınızı girin.')
    .min(3, 'Kullanıcı adı en az 3 karakter olmalıdır.')
    .max(64, 'Kullanıcı adı en fazla 64 karakter olabilir.'),
  password: z
    .string()
    .min(1, 'Lütfen şifrenizi girin.')
    .min(8, 'Şifre en az 8 karakter olmalıdır.'),
})

type FormValues = z.infer<typeof formSchema>

type UserAuthFormProps = React.HTMLAttributes<HTMLFormElement> & {
  redirectTo?: string
}

export function UserAuthForm({
  className,
  redirectTo,
  ...props
}: UserAuthFormProps) {
  const [pending, setPending] = useState<'form' | 'demo' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: '', password: '' },
  })

  function completeSignIn(session: AuthSession) {
    setSession(session)
    toast.success(`Hoş geldiniz, ${session.user.displayName}`)
    navigate({ to: safeRedirectPath(redirectTo), replace: true })
  }

  async function onSubmit(values: FormValues) {
    setError(null)
    setPending('form')
    try {
      completeSignIn(await authService.login(values))
    } catch (err) {
      setError(
        err instanceof AuthUnavailableError
          ? err.message
          : 'Giriş başarısız. Kullanıcı adı veya şifre hatalı olabilir.'
      )
    } finally {
      // Şifre hiçbir durumda bellekte/formda tutulmaya devam etmez.
      form.resetField('password')
      setPending(null)
    }
  }

  async function onDemoSignIn() {
    setError(null)
    setPending('demo')
    try {
      completeSignIn(await authService.loginDemo())
    } finally {
      setPending(null)
    }
  }

  const isBusy = pending !== null

  return (
    <div className='grid gap-5'>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className={cn('grid gap-4', className)}
          noValidate
          {...props}
        >
          <FormField
            control={form.control}
            name='username'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Kullanıcı adı</FormLabel>
                <FormControl>
                  <Input
                    placeholder='ornek.kullanici'
                    autoComplete='username'
                    autoCapitalize='none'
                    spellCheck={false}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name='password'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Şifre</FormLabel>
                <FormControl>
                  <PasswordInput
                    placeholder='••••••••'
                    autoComplete='current-password'
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {error && (
            <Alert variant='destructive' role='alert'>
              <TriangleAlert />
              <AlertTitle>Giriş yapılamadı</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button type='submit' disabled={isBusy}>
            {pending === 'form' ? (
              <Loader2 className='animate-spin' />
            ) : (
              <LogIn />
            )}
            Giriş Yap
          </Button>
        </form>
      </Form>

      <div className='relative'>
        <div className='absolute inset-0 flex items-center'>
          <span className='w-full border-t' />
        </div>
        <div className='relative flex justify-center text-xs uppercase'>
          <span className='bg-background px-2 text-muted-foreground'>veya</span>
        </div>
      </div>

      <div className='grid gap-3 rounded-lg border border-dashed border-amber-500/50 bg-amber-500/5 p-4'>
        <div className='flex items-start gap-2 text-sm'>
          <FlaskConical className='mt-0.5 size-4 shrink-0 text-amber-600 dark:text-amber-400' />
          <div className='space-y-1'>
            <p className='font-medium'>Demo Modu</p>
            <p className='text-muted-foreground'>
              Yalnızca prototip incelemesi içindir. Kimlik doğrulaması yapılmaz
              ve <strong>gerçek güvenlik sağlamaz</strong>. Şifre veya kimlik
              bilgisi saklanmaz.
            </p>
          </div>
        </div>
        <Button
          type='button'
          variant='outline'
          onClick={onDemoSignIn}
          disabled={isBusy}
        >
          {pending === 'demo' ? (
            <Loader2 className='animate-spin' />
          ) : (
            <FlaskConical />
          )}
          Demo Modu ile Giriş
        </Button>
      </div>
    </div>
  )
}
