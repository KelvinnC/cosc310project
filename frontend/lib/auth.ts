/**
 * Decodes a JWT token and extracts the user ID from the payload.
 * @param token - The JWT access token string
 * @returns The user ID if found, or null if the token is invalid
 */
export function getUserIdFromToken(token: string | null | undefined): string | null {
  if (!token || typeof token !== 'string') {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.user_id || payload.sub || null;
  } catch {
    return null;
  }
}
