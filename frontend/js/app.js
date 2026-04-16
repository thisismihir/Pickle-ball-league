// Common utilities and helpers

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="loading">Loading...</div>`;
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="alert alert-error">${message}</div>`;
    }
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="alert alert-success">${message}</div>`;
    }
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'approved':
        case 'confirmed':
            return 'badge-success';
        case 'pending':
        case 'submitted':
            return 'badge-warning';
        case 'rejected':
            return 'badge-danger';
        default:
            return 'badge-info';
    }
}