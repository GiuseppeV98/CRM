// src/utils/csrf.js
export function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, cookie.indexOf('=')).trim() === 'csrftoken') {
                cookieValue = decodeURIComponent(cookie.substring(cookie.indexOf('=') + 1));
                break;
            }
        }
    }
    return cookieValue;
}
