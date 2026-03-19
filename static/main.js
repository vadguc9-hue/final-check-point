// EcoMaterial Hub - Main JavaScript
class EcoMaterialHub {
    constructor() {
        this.searchTimeout = null;
        this.searchInput = null;
        this.productGrid = null;
        this.loadingSpinner = null;
        this.categoryFilter = null;
        this.init();
    }

    init() {
        this.setupElements();
        this.setupSearch();
        this.setupMobileNav();
        this.setupFlashMessages();
        this.setupFavoriteButtons();
    }

    setupElements() {
        this.searchInput = document.getElementById('search-input');
        this.featuredProductsGrid = document.getElementById('featured-products-grid');
        this.searchResultsGrid = document.getElementById('search-results-grid');
        this.searchResultsSection = document.getElementById('search-results-section');
        this.loadingSpinner = document.getElementById('search-loading');
        this.categoryFilter = document.getElementById('category-filter');
    }

    setupSearch() {
        if (!this.searchInput || !this.searchResultsGrid) return;

        // Debounced search input
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length === 0) {
                this.showOriginalProducts();
                return;
            }
            
            if (query.length < 2) return; // Don't search for very short queries
            
            this.showLoading();
            
            // Debounce search (wait 300ms after user stops typing)
            this.searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        });

        // Category filter change
        if (this.categoryFilter) {
            this.categoryFilter.addEventListener('change', () => {
                const query = this.searchInput.value.trim();
                if (query.length >= 2) {
                    this.showLoading();
                    this.performSearch(query);
                }
            });
        }
    }

    async performSearch(query) {
        try {
            const categoryId = this.categoryFilter ? this.categoryFilter.value : '';
            let url = `/api/search?q=${encodeURIComponent(query)}`;
            if (categoryId) {
                url += `&category=${categoryId}`;
            }
            
            const response = await fetch(url);
            const products = await response.json();
            
            this.displaySearchResults(products);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displaySearchResults(products) {
        if (!this.searchResultsGrid) return;

        // Show search results section
        if (this.searchResultsSection) {
            this.searchResultsSection.style.display = 'block';
        }

        if (products.length === 0) {
            this.searchResultsGrid.innerHTML = `
                <div class="col-12">
                    <div class="card text-center">
                        <div class="card-body py-5">
                            <i class="fas fa-search fa-3x text-muted mb-3"></i>
                            <h4>No products found</h4>
                            <p class="text-muted">Try adjusting your search terms</p>
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        const productsHTML = products.map(product => this.createProductCard(product)).join('');
        this.searchResultsGrid.innerHTML = productsHTML;
    }

    createProductCard(product) {
        const isFavorited = product.is_favorited;
        const favoriteIcon = isFavorited ? 'fas fa-heart text-danger' : 'far fa-heart';
        const favoriteText = isFavorited ? 'Favorited' : 'Add to Favorites';
        
        return `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card h-100 product-card" data-product-id="${product.id}">
                    ${product.photo_filename ? 
                        `<img src="/static/uploads/${product.photo_filename}" alt="${product.title}" class="card-img-top" style="height: 200px; object-fit: cover;">` :
                        `<div class="card-img-top d-flex align-items-center justify-content-center bg-light" style="height: 200px;">
                            <i class="fas fa-box fa-3x text-success"></i>
                        </div>`
                    }
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${this.escapeHtml(product.title)}</h5>
                        <p class="card-text text-muted">${this.escapeHtml(product.description)}</p>
                        <div class="mt-auto">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="h5 text-success mb-0">$${product.price.toFixed(2)}</span>
                                <span class="badge bg-secondary">${this.escapeHtml(product.category)}</span>
                            </div>
                            <div class="d-flex gap-2">
                                <a href="/toggle_favorite/${product.id}" class="btn btn-sm btn-outline-danger favorite-btn">
                                    <i class="${favoriteIcon}"></i> ${favoriteText}
                                </a>
                                <a href="/product/${product.id}" class="btn btn-sm btn-success">
                                    <i class="fas fa-eye"></i> View Details
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    showOriginalProducts() {
        // Hide search results section
        if (this.searchResultsSection) {
            this.searchResultsSection.style.display = 'none';
        }
        // Clear search results grid
        if (this.searchResultsGrid) {
            this.searchResultsGrid.innerHTML = '';
        }
    }

    showLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = 'block';
        }
    }

    hideLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = 'none';
        }
    }

    showError(message) {
        this.showFlashMessage(message, 'danger');
    }

    setupMobileNav() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.mobile-nav .nav-item');
        
        navItems.forEach(item => {
            if (item.getAttribute('href') === currentPath) {
                item.classList.add('active');
            }
        });
    }

    setupFlashMessages() {
        // Auto-dismiss flash messages after 5 seconds
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            setTimeout(() => {
                if (message.parentNode) {
                    message.style.transition = 'opacity 0.3s ease';
                    message.style.opacity = '0';
                    setTimeout(() => message.remove(), 300);
                }
            }, 5000);
        });
    }

    setupFavoriteButtons() {
        // Use event delegation for dynamic favorite buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.favorite-btn')) {
                e.preventDefault();
                const btn = e.target.closest('.favorite-btn');
                const href = btn.getAttribute('href');
                console.log('Favorite button clicked:', href);
                
                if (!href) {
                    console.error('No href found on favorite button');
                    return;
                }
                
                const match = href.match(/toggle_favorite\/(\d+)/);
                if (!match) {
                    console.error('Invalid href format:', href);
                    return;
                }
                
                const productId = match[1];
                console.log('Product ID:', productId);
                this.toggleFavorite(btn, productId);
            }
        });
    }

    async toggleFavorite(button, productId) {
        console.log('Toggling favorite for product:', productId);
        
        try {
            // Get CSRF token
            const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                              document.querySelector('input[name=csrf_token]')?.value;
            
            console.log('CSRF token found:', !!csrfToken);
            
            const headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
            
            console.log('Sending request to:', `/toggle_favorite/${productId}`);
            
            const response = await fetch(`/toggle_favorite/${productId}`, {
                method: 'POST',
                headers: headers,
                credentials: 'same-origin'
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                // Toggle the heart state without page reload
                if (button.innerHTML.includes('far fa-heart')) {
                    // Add to favorites
                    button.innerHTML = '<i class="fas fa-heart text-danger"></i> Favorited';
                } else {
                    // Remove from favorites
                    button.innerHTML = '<i class="far fa-heart"></i> Add to Favorites';
                }
                
                // Show flash message
                this.showFlashMessage(data.message, data.action === 'added' ? 'success' : 'info');
            } else {
                console.error('Failed to toggle favorite:', data);
                this.showFlashMessage('Failed to toggle favorite', 'danger');
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
            this.showFlashMessage('Error toggling favorite', 'danger');
        }
    }

    showFlashMessage(message, type) {
        // Create flash message element
        const flashDiv = document.createElement('div');
        flashDiv.className = `alert alert-${type} alert-dismissible fade show`;
        flashDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(flashDiv, container.firstChild);
            
            // Auto-dismiss after 3 seconds
            setTimeout(() => {
                if (flashDiv.parentNode) {
                    flashDiv.remove();
                }
            }, 3000);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    window.ecoHub = new EcoMaterialHub();
});

// Export for potential use in other scripts
window.EcoMaterialHub = EcoMaterialHub;
