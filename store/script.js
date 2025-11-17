// App Data
const appDatabase = [
    {
        id: 'notify-soul',
        name: 'Notify Soul',
        description: 'Premium notification scheduling and automation app.',
        longDescription: 'Premium notification scheduling and automation app. Manage your notifications intelligently with advanced scheduling features and smart automation.',
        icon: '<circle cx="50" cy="50" r="45" fill="#0077ff"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">N</text>',
        banner: 'linear-gradient(135deg, #0077ff 0%, #0099cc 100%)',
        version: '1.0.0',
        size: '24 MB',
        updated: 'Nov 2025',
        downloadPath: 'apk/apk/notifysoul.apk'
    },
    {
        id: 'cipher-guard',
        name: 'Cipher Guard',
        description: 'Advanced security and encryption management.',
        longDescription: 'Advanced security and encryption management. Protect your sensitive data with military-grade encryption and smart security features.',
        icon: '<circle cx="50" cy="50" r="45" fill="#1a1a2e"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">C</text>',
        banner: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        version: '2.1.0',
        size: '32 MB',
        updated: 'Oct 2025',
        downloadPath: 'apk/cipher-guard.apk'
    },
    {
        id: 'focus-flow',
        name: 'Focus Flow',
        description: 'Productivity tool with smart time management.',
        longDescription: 'Productivity tool with smart time management. Boost your productivity with intelligent task management and time tracking.',
        icon: '<circle cx="50" cy="50" r="45" fill="#0099cc"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">F</text>',
        banner: 'linear-gradient(135deg, #0099cc 0%, #00ccff 100%)',
        version: '1.5.2',
        size: '18 MB',
        updated: 'Sep 2025',
        downloadPath: 'apk/focus-flow.apk'
    },
    {
        id: 'pixel-studio',
        name: 'Pixel Studio',
        description: 'Creative design and image editing suite.',
        longDescription: 'Professional creative design and image editing suite. Create stunning visuals with powerful tools and intuitive interface.',
        icon: '<circle cx="50" cy="50" r="45" fill="#ff6b9d"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">P</text>',
        banner: 'linear-gradient(135deg, #ff6b9d 0%, #ff8fab 100%)',
        version: '3.0.1',
        size: '56 MB',
        updated: 'Aug 2025',
        downloadPath: 'apk/pixel-studio.apk'
    },
    {
        id: 'code-vault',
        name: 'Code Vault',
        description: 'Secure code snippets and developer tools.',
        longDescription: 'Secure code snippets and developer tools. Store and organize your code securely with cloud sync and advanced search.',
        icon: '<circle cx="50" cy="50" r="45" fill="#00b894"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">V</text>',
        banner: 'linear-gradient(135deg, #00b894 0%, #00e676 100%)',
        version: '1.2.0',
        size: '12 MB',
        updated: 'Nov 2025',
        downloadPath: 'apk/code-vault.apk'
    },
    {
        id: 'mind-map',
        name: 'Mind Map',
        description: 'Visual thinking and idea organization app.',
        longDescription: 'Visual thinking and idea organization app. Create beautiful mind maps and organize your thoughts with ease.',
        icon: '<circle cx="50" cy="50" r="45" fill="#a29bfe"/><text x="50" y="60" font-size="40" fill="white" text-anchor="middle" font-weight="bold">M</text>',
        banner: 'linear-gradient(135deg, #a29bfe 0%, #b3a8ff 100%)',
        version: '2.0.0',
        size: '28 MB',
        updated: 'Jul 2025',
        downloadPath: 'apk/mind-map.apk'
    }
];

// DOM Elements
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
const navLinks = document.querySelectorAll('[data-page]');
const pages = document.querySelectorAll('.page');
const appsGrid = document.getElementById('appsGrid');
const searchInput = document.getElementById('searchInput');
const contactForm = document.getElementById('contactForm');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    renderAppsGrid();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Navigation
    hamburger?.addEventListener('click', toggleMobileMenu);
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            navigateTo(page);
            closeMenu();
        });
    });

    // Search
    searchInput?.addEventListener('input', filterApps);

    // Contact Form
    contactForm?.addEventListener('submit', handleContactSubmit);

    // Featured Section Slider
    setupSlider();

    // App Card Clicks
    document.addEventListener('click', (e) => {
        if (e.target.closest('.featured-app-card')) {
            const button = e.target.closest('.view-button');
            if (button) {
                const appId = button.dataset.app;
                showAppDetails(appId);
                navigateTo('app-details');
            }
        }
    });

    // Download buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('download-button')) {
            const appCard = e.target.closest('.app-card');
            if (appCard) {
                const appTitle = appCard.querySelector('.app-card-title').textContent;
                const appId = appCard.dataset.appId;
                downloadApp(appId);
            }
        }
    });

    // App details download
    const detailsDownloadBtn = document.getElementById('detailsDownloadBtn');
    if (detailsDownloadBtn) {
        detailsDownloadBtn.addEventListener('click', () => {
            const appTitle = document.getElementById('detailsTitle').textContent;
            const appId = document.getElementById('detailsDownloadBtn').dataset.appId;
            downloadApp(appId);
        });
    }
}

// Navigation
function navigateTo(pageId) {
    // Hide all pages
    pages.forEach(page => page.classList.remove('active'));
    
    // Show selected page
    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.classList.add('active');
        window.scrollTo(0, 0);
    }
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    hamburger.classList.toggle('active');
    mobileMenu.classList.toggle('active');
}

function closeMenu() {
    hamburger.classList.remove('active');
    mobileMenu.classList.remove('active');
}

// Render Apps Grid
function renderAppsGrid() {
    appsGrid.innerHTML = '';
    
    appDatabase.forEach(app => {
        const appCard = document.createElement('div');
        appCard.className = 'app-card';
        appCard.dataset.appId = app.id;
        appCard.innerHTML = `
            <div class="app-card-image" style="background: ${app.banner}">
                <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    ${app.icon}
                </svg>
            </div>
            <div class="app-card-content">
                <h3 class="app-card-title">${app.name}</h3>
                <p class="app-card-description">${app.description}</p>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="download-button" style="flex: 1;">Download</button>
                    <button class="view-button" style="flex: 1; background: var(--gray-light); color: var(--text-dark);" onclick="showAppDetails('${app.id}'); navigateTo('app-details');">Details</button>
                </div>
            </div>
        `;
        appsGrid.appendChild(appCard);
    });
}

// Filter Apps
function filterApps() {
    const searchTerm = searchInput.value.toLowerCase();
    const appCards = document.querySelectorAll('.app-card');
    
    appCards.forEach(card => {
        const title = card.querySelector('.app-card-title').textContent.toLowerCase();
        const description = card.querySelector('.app-card-description').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || description.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// Show App Details
function showAppDetails(appId) {
    const app = appDatabase.find(a => a.id === appId);
    
    if (!app) return;

    document.getElementById('detailsTitle').textContent = app.name;
    document.getElementById('detailsSubtitle').textContent = 'by Clay Group';
    document.getElementById('detailsVersion').textContent = app.version;
    document.getElementById('detailsSize').textContent = app.size;
    document.getElementById('detailsUpdated').textContent = app.updated;
    document.getElementById('detailsDescription').textContent = app.longDescription;

    // Update logo
    const detailsLogo = document.getElementById('detailsLogo');
    detailsLogo.innerHTML = app.icon;

    // Update download button
    const detailsDownloadBtn = document.getElementById('detailsDownloadBtn');
    detailsDownloadBtn.dataset.appId = appId;
    detailsDownloadBtn.textContent = `Download ${app.name}`;
}

// Download App
function downloadApp(appId) {
    const app = appDatabase.find(a => a.id === appId);
    
    if (!app) return;

    // Create a link and trigger download
    const link = document.createElement('a');
    link.href = app.downloadPath;
    link.download = `${app.id}.apk`;
    
    // Check if file exists by attempting to fetch
    fetch(app.downloadPath, { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                link.click();
                showDownloadNotification(app.name);
            } else {
                showDownloadNotification(app.name, false);
            }
        })
        .catch(() => {
            // If file check fails, try the download anyway
            link.click();
            showDownloadNotification(app.name);
        });
}

// Download Notification
function showDownloadNotification(appName, success = true) {
    const message = success ? 
        `${appName} download started...` : 
        `${appName} file not found. Please try again later.`;
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${success ? '#0077ff' : '#ff4757'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Setup Slider
function setupSlider() {
    const slider = document.querySelector('.featured-apps-slider');
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    
    if (!slider) return;
    
    const scrollAmount = 320; // Card width + gap
    
    leftArrow?.addEventListener('click', () => {
        slider.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
    
    rightArrow?.addEventListener('click', () => {
        slider.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
}

// Handle Contact Form Submit
function handleContactSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('contactName').value;
    const email = document.getElementById('contactEmail').value;
    const message = document.getElementById('contactMessage').value;
    
    if (name && email && message) {
        // Show success message
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: #0077ff;
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = `Thank you ${name}! We've received your message and will get back to you soon.`;
        
        document.body.appendChild(notification);
        
        // Reset form
        contactForm.reset();
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
}

// Add animations to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Start on home page
window.addEventListener('load', () => {
    navigateTo('home');
});
