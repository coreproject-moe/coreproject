// Function to update visibility based on current body data attribute
function updateVisibility(e) {
    const body = document.body;
    const mediaQuery = body.getAttribute('data-md-color-media');

    if (!mediaQuery) return;

    const mqList = window.matchMedia(mediaQuery);
    const isDark = e ? e.matches : mqList.matches;

    // Show/hide .dark elements
    document.querySelectorAll('.dark').forEach(el => {
        el.style.display = isDark ? '' : 'none';
    });

    // Show/hide .light elements
    document.querySelectorAll('.light').forEach(el => {
        el.style.display = isDark ? 'none' : '';
    });
}

// Initial check
updateVisibility();

// Listen for system color changes
function attachMediaListener() {
    const body = document.body;
    const mediaQuery = body.getAttribute('data-md-color-media');
    if (!mediaQuery) return;

    const mqList = window.matchMedia(mediaQuery);
    mqList.addEventListener('change', updateVisibility);
}

// Attach listener initially
attachMediaListener();

// Observe body attribute changes
const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-media') {
            // Reapply visibility
            updateVisibility();
            // Reattach listener to the new media query
            attachMediaListener();
        }
    });
});

// Start observing
observer.observe(document.body, { attributes: true });
