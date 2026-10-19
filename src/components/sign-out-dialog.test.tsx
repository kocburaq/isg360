import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render } from 'vitest-browser-react'
import { userEvent } from 'vitest/browser'
import { SignOutDialog } from './sign-out-dialog'

const navigate = vi.fn()
const clearSession = vi.fn()
const logout = vi.fn().mockResolvedValue(undefined)

const MOCK_HREF = '/cameras?camera=cam-01'
const MOCK_SESSION = { mode: 'demo' }

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: (selector: (s: unknown) => unknown) =>
    selector({ session: MOCK_SESSION, clearSession }),
}))

vi.mock('@/services/auth/auth-service', () => ({
  authService: { logout: (...args: unknown[]) => logout(...args) },
}))

vi.mock('@tanstack/react-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@tanstack/react-router')>()
  return {
    ...actual,
    useNavigate: () => navigate,
    useLocation: () => ({ href: MOCK_HREF }),
  }
})

describe('SignOutDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('logs out, clears the session and navigates to sign-in with current location as redirect', async () => {
    const { getByRole } = await render(
      <SignOutDialog open onOpenChange={vi.fn()} />
    )

    await userEvent.click(getByRole('button', { name: /^Çıkış Yap$/ }))

    await vi.waitFor(() => expect(clearSession).toHaveBeenCalledOnce())
    expect(logout).toHaveBeenCalledWith(MOCK_SESSION)
    expect(navigate).toHaveBeenCalledWith({
      to: '/sign-in',
      search: { redirect: MOCK_HREF },
      replace: true,
    })
  })

  it('does nothing when Vazgeç is clicked', async () => {
    const { getByRole } = await render(
      <SignOutDialog open onOpenChange={vi.fn()} />
    )

    await userEvent.click(getByRole('button', { name: /^Vazgeç$/ }))

    expect(clearSession).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
