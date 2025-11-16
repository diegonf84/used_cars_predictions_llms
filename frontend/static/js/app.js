// API Configuration
const API_BASE_URL = '/api/v1';

// DOM Elements
const form = document.getElementById('prediction-form');
const submitBtn = document.getElementById('submit-btn');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const resultsDiv = document.getElementById('results');
const newSearchBtn = document.getElementById('new-search-btn');

// Result Elements
const priceRangeEl = document.getElementById('price-range');
const friendlySummaryEl = document.getElementById('friendly-summary');
const warningsEl = document.getElementById('warnings');

// Event Listeners
form.addEventListener('submit', handleSubmit);
newSearchBtn.addEventListener('click', resetForm);

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();

    const description = document.getElementById('car-description').value.trim();

    if (!description) {
        showError('Please enter a car description');
        return;
    }

    // Show loading state
    hideAll();
    loadingDiv.classList.remove('hidden');
    submitBtn.disabled = true;

    try {
        // Call prediction API
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to get prediction');
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while processing your request');
    } finally {
        loadingDiv.classList.add('hidden');
        submitBtn.disabled = false;
    }
}

/**
 * Display prediction results
 */
function displayResults(data) {
    // Format price range
    const priceMin = formatCurrency(data.price_min);
    const priceMax = formatCurrency(data.price_max);

    // Update DOM
    priceRangeEl.textContent = `${priceMin} - ${priceMax}`;
    friendlySummaryEl.textContent = data.friendly_summary;

    // Display warnings if any
    if (data.warnings && data.warnings.length > 0) {
        warningsEl.innerHTML = `
            <h4>Considerations</h4>
            <ul>
                ${data.warnings.map(w => `<li>${w}</li>`).join('')}
            </ul>
        `;
    } else {
        warningsEl.innerHTML = '<h4>Considerations</h4><p>All information provided - no defaults used.</p>';
    }

    // Show results
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Show error message
 */
function showError(message) {
    hideAll();
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
}

/**
 * Hide all result sections
 */
function hideAll() {
    loadingDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    resultsDiv.classList.add('hidden');
}

/**
 * Reset form and UI
 */
function resetForm() {
    form.reset();
    hideAll();
    document.getElementById('car-description').focus();
}

/**
 * Format number as currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}

/**
 * Format number as percentage
 */
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
}

/**
 * Check API health on load
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (!data.model_loaded || !data.llm_configured) {
            console.warn('API services not fully initialized:', data);
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Run health check on page load
checkHealth();
