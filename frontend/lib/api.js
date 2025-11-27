export async function apiFetch(input, init = {}) {
  if (typeof window === 'undefined') {
    return fetch(input, init)
  }

  const token = localStorage.getItem('accessToken') || ''

  const headers = new Headers(init.headers || {})
  if (token) {
    const value = token.startsWith('Bearer ') ? token : `Bearer ${token}`
    headers.set('Authorization', value)
  }

  const finalInit = {
    credentials: init.credentials ?? 'same-origin',
    ...init,
    headers,
  }

  return fetch(input, finalInit)
}
