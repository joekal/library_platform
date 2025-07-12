// Library Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize accessibility features
    initializeAccessibility();
    
    // Initialize audio players
    initializeAudioPlayers();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize reading progress
    initializeReadingProgress();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
});

// Accessibility Functions
function initializeAccessibility() {
    // Apply user preferences from localStorage or server
    const preferences = getUserPreferences();
    applyAccessibilitySettings(preferences);
    
    // Keyboard navigation
    setupKeyboardNavigation();
    
    // Screen reader announcements
    setupScreenReaderAnnouncements();
    
    // Focus management
    setupFocusManagement();
}

function getUserPreferences() {
    // Get preferences from localStorage or make API call
    const stored = localStorage.getItem('userPreferences');
    if (stored) {
        return JSON.parse(stored);
    }
    
    // Default preferences
    return {
        fontSize: 'medium',
        theme: 'light',
        dyslexicFont: false,
        audioEnabled: true,
        reducedMotion: false
    };
}

function applyAccessibilitySettings(preferences) {
    const body = document.body;
    
    // Apply font size
    body.className = body.className.replace(/font-size-\w+/g, '');
    body.classList.add(`font-size-${preferences.fontSize}`);
    
    // Apply theme
    body.className = body.className.replace(/theme-\w+/g, '');
    body.classList.add(`theme-${preferences.theme}`);
    
    // Apply dyslexic font
    if (preferences.dyslexicFont) {
        body.classList.add('dyslexic-font');
    } else {
        body.classList.remove('dyslexic-font');
    }
    
    // Apply reduced motion
    if (preferences.reducedMotion) {
        document.documentElement.style.setProperty('--animation-duration', '0.01ms');
        document.documentElement.style.setProperty('--transition-duration', '0.01ms');
    }
}

function setupKeyboardNavigation() {
    // Skip link functionality
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.focus();
                target.scrollIntoView();
            }
        });
    }
    
    // Enhanced keyboard navigation for cards and interactive elements
    const interactiveElements = document.querySelectorAll('.book-card, .group-card, [data-keyboard-nav]');
    interactiveElements.forEach(element => {
        element.setAttribute('tabindex', '0');
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

function setupScreenReaderAnnouncements() {
    // Create live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-announcements';
    document.body.appendChild(liveRegion);
    
    // Function to announce messages
    window.announceToScreenReader = function(message) {
        const liveRegion = document.getElementById('live-announcements');
        liveRegion.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    };
}

function setupFocusManagement() {
    // Manage focus for modals and dynamic content
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstFocusable = this.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
    });
}

// Audio Player Functions
function initializeAudioPlayers() {
    const audioPlayers = document.querySelectorAll('.audio-player');
    audioPlayers.forEach(player => {
        setupAudioPlayer(player);
    });
}

function setupAudioPlayer(playerElement) {
    const audio = playerElement.querySelector('audio');
    const playButton = playerElement.querySelector('.play-button');
    const progressBar = playerElement.querySelector('.progress-fill');
    const currentTimeElement = playerElement.querySelector('.current-time');
    const durationElement = playerElement.querySelector('.duration');
    const volumeSlider = playerElement.querySelector('.volume-slider');
    
    if (!audio) return;
    
    let isPlaying = false;
    
    // Play/Pause functionality
    playButton.addEventListener('click', function() {
        if (isPlaying) {
            audio.pause();
            this.innerHTML = '<i class="fas fa-play"></i>';
            announceToScreenReader('Audio paused');
        } else {
            audio.play();
            this.innerHTML = '<i class="fas fa-pause"></i>';
            announceToScreenReader('Audio playing');
        }
        isPlaying = !isPlaying;
    });
    
    // Progress tracking
    audio.addEventListener('timeupdate', function() {
        const progress = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = progress + '%';
        
        if (currentTimeElement) {
            currentTimeElement.textContent = formatTime(audio.currentTime);
        }
    });
    
    // Duration display
    audio.addEventListener('loadedmetadata', function() {
        if (durationElement) {
            durationElement.textContent = formatTime(audio.duration);
        }
    });
    
    // Volume control
    if (volumeSlider) {
        volumeSlider.addEventListener('input', function() {
            audio.volume = this.value / 100;
        });
    }
    
    // Keyboard controls
    audio.addEventListener('keydown', function(e) {
        switch(e.key) {
            case ' ':
                e.preventDefault();
                playButton.click();
                break;
            case 'ArrowLeft':
                audio.currentTime = Math.max(0, audio.currentTime - 10);
                break;
            case 'ArrowRight':
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
                break;
        }
    });
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Search Functions
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            hideSearchResults();
        }
    });
}

function performSearch(query) {
    // Make API call to search endpoint
    fetch(`/api/books/?search=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('.search-results');
    if (!searchResults) return;
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-muted">No results found</div>';
    } else {
        const html = results.map(book => `
            <a href="/books/${book.id}/" class="search-result-item d-flex p-3 text-decoration-none">
                <img src="${book.cover_image}" alt="${book.title}" class="book-cover-small me-3">
                <div>
                    <div class="fw-bold">${book.title}</div>
                    <div class="text-muted small">${book.authors_display}</div>
                </div>
            </a>
        `).join('');
        searchResults.innerHTML = html;
    }
    
    searchResults.classList.add('show');
}

function hideSearchResults() {
    const searchResults = document.querySelector('.search-results');
    if (searchResults) {
        searchResults.classList.remove('show');
    }
}

// Reading Progress Functions
function initializeReadingProgress() {
    const progressElements = document.querySelectorAll('[data-reading-progress]');
    progressElements.forEach(element => {
        setupReadingProgress(element);
    });
}

function setupReadingProgress(element) {
    const bookId = element.dataset.bookId;
    const progressBar = element.querySelector('.progress-bar');
    
    // Load saved progress
    loadReadingProgress(bookId).then(progress => {
        updateProgressBar(progressBar, progress);
    });
    
    // Auto-save progress while reading
    if (element.classList.contains('reading-view')) {
        setupAutoSaveProgress(bookId);
    }
}

function loadReadingProgress(bookId) {
    return fetch(`/api/reading-history/?book=${bookId}`)
        .then(response => response.json())
        .then(data => {
            if (data.results.length > 0) {
                return data.results[0].progress_percentage;
            }
            return 0;
        })
        .catch(() => 0);
}

function updateProgressBar(progressBar, percentage) {
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
}

function setupAutoSaveProgress(bookId) {
    let saveTimeout;
    
    // Track scroll position for progress calculation
    window.addEventListener('scroll', function() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            const progress = calculateReadingProgress();
            saveReadingProgress(bookId, progress);
        }, 2000);
    });
}

function calculateReadingProgress() {
    const scrollTop = window.pageYOffset;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    return Math.min(100, Math.max(0, (scrollTop / docHeight) * 100));
}

function saveReadingProgress(bookId, progress) {
    fetch('/api/reading-history/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            book: bookId,
            progress_percentage: Math.round(progress),
            status: progress >= 100 ? 'completed' : 'reading'
        })
    }).catch(error => {
        console.error('Error saving progress:', error);
    });
}

// Bootstrap Components
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Utility Functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Settings Management
function updateUserPreferences(preferences) {
    // Save to localStorage
    localStorage.setItem('userPreferences', JSON.stringify(preferences));
    
    // Apply immediately
    applyAccessibilitySettings(preferences);
    
    // Send to server
    fetch('/api/auth/preferences/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(preferences)
    }).catch(error => {
        console.error('Error saving preferences:', error);
    });
}

// Export functions for use in other scripts
window.LibraryPlatform = {
    updateUserPreferences,
    announceToScreenReader,
    formatTime,
    debounce
};