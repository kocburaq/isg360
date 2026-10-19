import { useNavigate, useLocation } from '@tanstack/react-router'
import { authService } from '@/services/auth/auth-service'
import { useAuthStore } from '@/stores/auth-store'
import { ConfirmDialog } from '@/components/confirm-dialog'

interface SignOutDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SignOutDialog({ open, onOpenChange }: SignOutDialogProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const session = useAuthStore((s) => s.session)
  const clearSession = useAuthStore((s) => s.clearSession)

  const handleSignOut = async () => {
    try {
      await authService.logout(session)
    } finally {
      clearSession()
      // Tekrar girişte kullanıcı aynı sayfaya dönebilsin
      navigate({
        to: '/sign-in',
        search: { redirect: location.href },
        replace: true,
      })
    }
  }

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      title='Çıkış yap'
      desc='Oturumunuzu kapatmak istediğinize emin misiniz? Sisteme erişmek için yeniden giriş yapmanız gerekecek.'
      confirmText='Çıkış Yap'
      cancelBtnText='Vazgeç'
      destructive
      handleConfirm={handleSignOut}
      className='sm:max-w-sm'
    />
  )
}
