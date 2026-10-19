import { toast } from 'sonner'
import { getApiErrorMessage } from './api-error'

export function handleServerError(error: unknown) {
  if (import.meta.env.DEV) {
    // eslint-disable-next-line no-console
    console.log(error)
  }

  let errMsg = 'Bir hata oluştu.'

  if (
    error &&
    typeof error === 'object' &&
    'status' in error &&
    Number(error.status) === 204
  ) {
    errMsg = 'İçerik bulunamadı.'
  }

  errMsg = getApiErrorMessage(error) ?? errMsg

  toast.error(errMsg)
}
