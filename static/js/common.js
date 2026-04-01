/**
 * Shared utilities for the image uploader application.
 */

/**
 * Update active tab styling based on current page.
 */
function updateTabStyles() {
    const uploadTab = document.getElementById('upload-tab-btn');
    const imagesTab = document.getElementById('images-tab-btn');
    const dbGalleryTab = document.getElementById('images-tab-btn');

    if (!uploadTab || !imagesTab) return;

    const path = window.location.pathname;

    uploadTab.classList.remove('upload_tab--active');
    imagesTab.classList.remove('upload_tab--active');
    if (dbGalleryTab) dbGalleryTab.classList.remove('upload_tab--active');

    if (path.includes('images-list')) {
        if (dbGalleryTab) dbGalleryTab.classList.add('upload_tab--active');
    } else if (path.includes('images')) {
        imagesTab.classList.add('upload_tab--active');
    } else {
        uploadTab.classList.add('upload_tab--active');
    }
}

/**
 * Register keyboard shortcuts: Escape/F5 redirect to the given URL.
 */
function registerKeyboardShortcuts(redirectUrl) {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' || event.key === 'F5') {
            event.preventDefault();
            window.location.href = redirectUrl;
        }
    });
}

/**
 * Copy text to clipboard with fallback for non-secure (HTTP) contexts.
 * Returns a Promise that resolves on success.
 */
// Navigate to DB Gallery page
const dbGalleryBtn = document.getElementById('db-gallery-tab-btn');
if (dbGalleryBtn) {
    dbGalleryBtn.addEventListener('click', () => {
        window.location.href = '/images-list';
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    }

    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return Promise.resolve();
    } catch (err) {
        document.body.removeChild(textarea);
        return Promise.reject(err);
    }
}
