// API Helper Functions
const API_BASE = '/api';

async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        },
        credentials: 'same-origin',
        cache: 'no-store', // Prevent caching completely
    };
    
    const response = await fetch(`${API_BASE}${url}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    });
    
    // Handle 304 Not Modified - force a new request
    if (response.status === 304) {
        // Retry with no-cache headers
        const retryResponse = await fetch(`${API_BASE}${url}`, {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
            },
            cache: 'no-store',
        });
        
        if (!retryResponse.ok) {
            const error = await retryResponse.json().catch(() => ({ detail: 'Wystąpił błąd' }));
            throw new Error(error.detail || `HTTP ${retryResponse.status}`);
        }
        
        const text = await retryResponse.text();
        if (text) {
            return JSON.parse(text);
        }
        return {};
    }
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Wystąpił błąd' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    const text = await response.text();
    if (text) {
        return JSON.parse(text);
    }
    
    return {};
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Format date helper
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL');
}

// Format status badge
function getStatusBadge(status, type = 'project') {
    const statusMap = {
        project: {
            planned: 'badge-info',
            active: 'badge-success',
            on_hold: 'badge-warning',
            done: 'badge-primary',
            archived: 'badge-neutral',
        },
        task: {
            todo: 'badge-ghost',
            in_progress: 'badge-info',
            review: 'badge-warning',
            done: 'badge-success',
            blocked: 'badge-error',
        },
    };
    
    const statusLabels = {
        project: {
            planned: 'Planowany',
            active: 'Aktywny',
            on_hold: 'Wstrzymany',
            done: 'Zakończony',
            archived: 'Zarchiwizowany',
        },
        task: {
            todo: 'Do zrobienia',
            in_progress: 'W toku',
            review: 'Weryfikacja',
            done: 'Zrobione',
            blocked: 'Zablokowane',
        },
    };
    
    const className = statusMap[type]?.[status] || 'badge-ghost';
    const label = statusLabels[type]?.[status] || status;
    
    return `<span class="badge ${className}">${label}</span>`;
}

// Format priority badge
function getPriorityBadge(priority) {
    const priorityMap = {
        1: { class: 'badge-ghost', label: 'Niski' },
        2: { class: 'badge-info', label: 'Średni' },
        3: { class: 'badge-warning', label: 'Wysoki' },
        4: { class: 'badge-error', label: 'Krytyczny' },
    };
    
    const p = priorityMap[priority] || priorityMap[2];
    return `<span class="badge ${p.class}">${p.label}</span>`;
}

// Export for use in other scripts
window.WorklyAPI = {
    request: apiRequest,
    formatDate,
    getStatusBadge,
    getPriorityBadge,
};

