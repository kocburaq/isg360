import { describe, expect, it } from 'vitest'
import { safeRedirectPath } from './safe-redirect'

describe('safeRedirectPath', () => {
  it('falls back to "/" when empty', () => {
    expect(safeRedirectPath(undefined)).toBe('/')
    expect(safeRedirectPath('')).toBe('/')
  })

  it('keeps internal paths including query and hash', () => {
    expect(safeRedirectPath('/cameras?camera=cam-01#x')).toBe(
      '/cameras?camera=cam-01#x'
    )
  })

  it('rejects external and protocol-relative URLs', () => {
    expect(safeRedirectPath('https://evil.example/phish')).toBe('/')
    expect(safeRedirectPath('//evil.example/phish')).toBe('/')
  })

  it('does not redirect back to the sign-in page', () => {
    expect(safeRedirectPath('/sign-in?redirect=/')).toBe('/')
  })
})
