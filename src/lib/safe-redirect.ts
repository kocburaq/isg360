/**
 * Giriş sonrası yönlendirmenin yalnızca uygulama içi bir yola yapılmasını sağlar
 * (açık yönlendirme / open redirect saldırılarını engeller).
 */
export function safeRedirectPath(redirect: string | undefined): string {
  if (!redirect) return '/'
  try {
    const url = new URL(redirect, window.location.origin)
    if (url.origin !== window.location.origin) return '/'
    if (url.pathname.startsWith('/sign-in')) return '/'
    return `${url.pathname}${url.search}${url.hash}`
  } catch {
    return '/'
  }
}
