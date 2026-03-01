function checkAuth() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    return token && user ? JSON.parse(user) : null;
}

function isLoggedIn() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    return !!(token && user);
}

function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function getDisplayName(user) {
    if (!user || !user.email) {
        return user?.username?.charAt(0).toUpperCase() || 'U';
    }

    // Extract name from email (part before @)
    const emailName = user.email.split('@')[0];

    // Get initials - first letter of each part separated by . or _
    const parts = emailName.split(/[._]/);
    let initials = parts.map(part => part.charAt(0).toUpperCase()).join('');

    // If only one part or too many, just use first letter
    if (initials.length > 3 || initials.length === 0) {
        initials = emailName.charAt(0).toUpperCase();
    }

    return initials;
}

function requireAuth() {
    const user = checkAuth();
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    return user;
}

function requireAdmin() {
    const user = requireAuth();
    if (user && user.role !== 'admin') {
        window.location.href = 'dashboard.html';
        return null;
    }
    return user;
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Clear any cached data
    sessionStorage.clear();

    // Redirect to homepage (login page for logged out users)
    window.location.href = 'index.html';
}

function updateNavbar() {
    const user = checkAuth();

    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const userInfo = document.getElementById('userInfo');
    const logoutBtn = document.getElementById('logoutBtn');
    const fixturesLink = document.getElementById('fixturesLink');
    const adminLink = document.getElementById('adminLink');

    if (user) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (registerBtn) registerBtn.style.display = 'none';

        if (userInfo) {
            userInfo.style.display = 'inline';
            userInfo.textContent = getDisplayName(user);
        }

        if (logoutBtn) {
            logoutBtn.style.display = 'inline-block';
            logoutBtn.addEventListener('click', logout);
        }

        if (fixturesLink) fixturesLink.style.display = 'inline';
        if (adminLink && user.role === 'admin') {
            adminLink.style.display = 'inline';
        }

    } else {
        if (loginBtn) loginBtn.style.display = 'inline-block';
        if (registerBtn) registerBtn.style.display = 'inline-block';
        if (userInfo) userInfo.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (fixturesLink) fixturesLink.style.display = 'none';
        if (adminLink) adminLink.style.display = 'none';
    }
}

// Update navbar on page load
document.addEventListener('DOMContentLoaded', updateNavbar);