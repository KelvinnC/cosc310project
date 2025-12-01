function decodeToken(token) {
    try {

        const parts = token.split('.')
        const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const padded = payload + '='.repeat((4 - (payload.length % 4)) % 4);
        const decoded = JSON.parse(atob(padded))
        return decoded
    } catch (err) {
        console.error('decodeToken error:', err.message);
        return null
    }
}

export default decodeToken