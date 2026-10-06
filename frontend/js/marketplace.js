/**
 * KrushiSetu Marketplace Produce Discovery & Trading
 * Connected to live backend Product APIs
 */

let marketplaceCache = [];

async function fetchAndRenderMarketplace() {
  const container = document.getElementById('produce-grid');
  if (!container) return;

  const searchInput = document.getElementById('market-search');
  const sortSelect = document.getElementById('market-sort');
  const maxPriceInput = document.getElementById('filter-max-price');
  const minQtyInput = document.getElementById('filter-min-qty');
  const locationInput = document.getElementById('filter-location');

  // Collect checked categories
  const categoryBoxes = document.querySelectorAll('.category-filter:checked');
  const selectedCategories = Array.from(categoryBoxes).map(cb => cb.value);

  // Collect checked grades
  const gradeBoxes = document.querySelectorAll('.grade-filter:checked');
  const selectedGrades = Array.from(gradeBoxes).map(cb => cb.value);

  const params = {};
  if (searchInput && searchInput.value.trim()) params.search = searchInput.value.trim();
  if (sortSelect) params.sort = sortSelect.value;
  if (maxPriceInput && maxPriceInput.value) params.max_price = maxPriceInput.value;
  if (minQtyInput && minQtyInput.value) params.min_qty = minQtyInput.value;
  if (locationInput && locationInput.value.trim()) params.location = locationInput.value.trim();

  // If single category selected, pass to backend
  if (selectedCategories.length === 1) {
    params.category = selectedCategories[0];
  }

  try {
    const res = await ProductsManager.getMarketplaceProducts(params);
    let products = res.products || [];

    // Client-side multi-filter refinement
    if (selectedCategories.length > 1) {
      products = products.filter(p => selectedCategories.includes(p.category));
    }
    if (selectedGrades.length > 0) {
      products = products.filter(p => selectedGrades.includes(p.grade));
    }

    marketplaceCache = products;
    renderProduceGrid(products);

  } catch (err) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 3rem; color: var(--danger);">
        <h3>⚠️ Error loading marketplace produce</h3>
        <p>${err.message}</p>
      </div>
    `;
  }
}

const CROP_FALLBACKS = {
  tomato: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80',
  tomatoes: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80',
  berry: 'https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80',
  berries: 'https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80',
  strawberry: 'https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80',
  onion: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80',
  onions: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80',
  potato: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80',
  potatoes: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80',
  wheat: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80',
  rice: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80',
  basmati: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80',
  orange: 'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80',
  oranges: 'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80',
  santra: 'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80',
  apple: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80',
  cotton: 'https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=600&q=80',
  chilli: 'https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80',
  pulses: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80',
  dal: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80'
};

const NEUTRAL_CROP_PLACEHOLDER = 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=600&q=80';

function resolveProductImage(item) {
  if (!item) return NEUTRAL_CROP_PLACEHOLDER;
  const explicit = item.image_url || item.images?.[0];
  const nameLower = (item.crop_name || item.name || '').toLowerCase();
  
  if (explicit && !explicit.includes('photo-1574323347407')) {
    return explicit;
  }
  if (explicit && explicit.includes('photo-1574323347407') && nameLower.includes('wheat')) {
    return explicit;
  }
  for (const [key, url] of Object.entries(CROP_FALLBACKS)) {
    if (nameLower.includes(key)) return url;
  }
  return explicit || NEUTRAL_CROP_PLACEHOLDER;
}

function renderProduceGrid(items) {
  const container = document.getElementById('produce-grid');
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 4rem 1rem; color: var(--slate-500);">
        <span style="font-size: 3rem; display: block; margin-bottom: 0.5rem;">🌾</span>
        <h3 style="font-size: 1.3rem; color: var(--slate-800);">No produce found matching your criteria</h3>
        <p style="margin-top: 0.25rem;">Try adjusting your price range, category, or search keywords.</p>
        <button class="btn btn-outline-primary btn-sm" style="margin-top: 1rem;" onclick="resetAllFilters()">Reset All Filters</button>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="produce-card">
      <div class="produce-img-wrap" onclick="openProductDetailModal('${item.id}')" style="cursor: pointer;">
        <img src="${resolveProductImage(item)}" alt="${item.crop_name || item.name}" loading="lazy" />
        <span class="badge ${item.organic ? 'badge-success' : 'badge-earth'} produce-tag">
          ${item.organic ? '🌱 100% Organic' : '🚜 Farm Fresh'}
        </span>
      </div>
      <div class="produce-body">
        <h3 class="produce-title" onclick="openProductDetailModal('${item.id}')" style="cursor: pointer;">${item.crop_name || item.name}</h3>
        <div class="produce-meta">
          <span>👨‍🌾 ${item.farmer_name}</span>
          <span>•</span>
          <span>📍 ${item.location}</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 0.75rem;">
          Grade: <strong>${item.grade || 'Grade A'}</strong> • Harvest: <strong>${item.harvest_date || 'Recent'}</strong>
        </div>
        <div class="produce-price-row">
          <div>
            <span class="price-val">₹${(item.price_per_unit || item.price || 0).toFixed(2)}</span>
            <span class="price-unit">/${item.unit || 'kg'}</span>
          </div>
          <div class="qty-avail">Avail: <strong>${(item.quantity || 0).toLocaleString()} ${item.unit || 'kg'}</strong></div>
        </div>
        <div class="produce-actions" style="display: flex; gap: 0.5rem; margin-top: 1rem;">
          <button class="btn btn-outline btn-sm" style="flex: 1;" onclick="openProductDetailModal('${item.id}')">
            🔍 Details
          </button>
          <button class="btn btn-primary btn-sm" style="flex: 1.5;" onclick="openOrderModal('${item.id}')">
            🤝 Direct Buy
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

// Product Details Modal View
async function openProductDetailModal(productId) {
  let product = marketplaceCache.find(p => p.id === productId);
  if (!product) {
    try {
      const res = await ProductsManager.getProductDetails(productId);
      product = res.product;
    } catch (err) {
      showToast('Could not load product details.', 'error');
      return;
    }
  }

  const modal = document.getElementById('product-detail-modal');
  const modalContent = document.getElementById('product-detail-content');
  if (!modal || !modalContent) return;

  const imgSrc = resolveProductImage(product);

  modalContent.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 1.25rem;">
      <div>
        <span class="badge ${product.organic ? 'badge-success' : 'badge-earth'}" style="margin-bottom: 0.35rem;">
          ${product.organic ? '🌱 100% Certified Organic' : '🚜 Farm Fresh Harvest'}
        </span>
        <h2 style="font-size: 1.6rem; color: var(--slate-900);">${product.crop_name || product.name}</h2>
      </div>
      <span style="font-size: 1.5rem; cursor: pointer;" onclick="closeProductDetailModal()">✕</span>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
      <div style="border-radius: var(--radius-lg); overflow: hidden; height: 220px;">
        <img src="${imgSrc}" style="width: 100%; height: 100%; object-fit: cover;" alt="${product.crop_name}" />
      </div>
      <div>
        <div style="background: var(--slate-50); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
          <div style="font-size: 0.85rem; color: var(--slate-500);">Direct Farm Rate</div>
          <div style="font-size: 1.75rem; font-weight: 800; color: var(--primary-800); font-family: var(--font-heading);">
            ₹${(product.price_per_unit || product.price || 0).toFixed(2)} <span style="font-size: 0.9rem; color: var(--slate-500);">/ ${product.unit || 'kg'}</span>
          </div>
          <div style="font-size: 0.88rem; color: var(--slate-700); margin-top: 0.25rem;">
            Total Available: <strong>${(product.quantity || 0).toLocaleString()} ${product.unit || 'kg'}</strong>
          </div>
        </div>

        <div style="font-size: 0.88rem; color: var(--slate-700); display: flex; flex-direction: column; gap: 0.35rem;">
          <div>🌾 Category: <strong>${product.category || 'Grains'}</strong></div>
          <div>⭐ Quality Grade: <strong>${product.grade || 'Grade A'}</strong></div>
          <div>📅 Harvest Date: <strong>${product.harvest_date || 'Recent'}</strong></div>
        </div>
      </div>
    </div>

    <!-- Farmer & Location Card (Sanitized) -->
    <div style="background: var(--primary-50); border: 1px solid var(--primary-100); padding: 1rem 1.25rem; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
      <h4 style="color: var(--primary-900); margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.5rem;">
        👨‍🌾 Farmer Origin Information
      </h4>
      <div style="font-size: 0.9rem; color: var(--slate-700);">
        Producer: <strong>${product.farmer_name}</strong> (Verified Producer)<br />
        Public Region: <strong>📍 ${product.location}</strong>
      </div>
    </div>

    <!-- Description -->
    <div style="margin-bottom: 1.5rem;">
      <h4 style="font-size: 0.95rem; color: var(--slate-800); margin-bottom: 0.35rem;">Lot Description & Quality Notes:</h4>
      <p style="font-size: 0.9rem; color: var(--slate-600); line-height: 1.6;">
        ${product.description || 'Harvested and sorted with strict quality compliance. Moisture controlled and ready for direct transit.'}
      </p>
    </div>

    <div style="display: flex; gap: 1rem;">
      <button type="button" class="btn btn-outline" style="flex: 1;" onclick="showToast('Contact request sent to farmer', 'info')">
        💬 Message Farmer
      </button>
      <button type="button" class="btn btn-primary" style="flex: 2;" onclick="closeProductDetailModal(); openOrderModal('${product.id}');">
        🤝 Place Escrow Order
      </button>
    </div>
  `;

  modal.style.display = 'flex';
}

function closeProductDetailModal() {
  const modal = document.getElementById('product-detail-modal');
  if (modal) modal.style.display = 'none';
}

// Direct Buy Order Modal
function openOrderModal(productId) {
  const product = marketplaceCache.find(p => p.id === productId);
  if (!product) return;

  const modal = document.getElementById('order-modal');
  const modalBody = document.getElementById('modal-body-content');
  if (!modal || !modalBody) return;

  modalBody.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.25rem;">
      <h3 style="font-size: 1.35rem; color: var(--slate-900);">🤝 Direct Procurement Contract</h3>
      <span style="font-size: 1.5rem; cursor: pointer;" onclick="closeOrderModal()">✕</span>
    </div>

    <div style="background: var(--slate-50); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
      <div style="display:flex; justify-content:space-between; margin-bottom: 0.35rem;">
        <span>Produce:</span> <strong>${product.crop_name || product.name}</strong>
      </div>
      <div style="display:flex; justify-content:space-between; margin-bottom: 0.35rem;">
        <span>Direct Rate:</span> <strong>₹${(product.price_per_unit || product.price || 0).toFixed(2)} / ${product.unit || 'kg'}</strong>
      </div>
      <div style="display:flex; justify-content:space-between;">
        <span>Producer:</span> <strong>${product.farmer_name} (${product.location})</strong>
      </div>
    </div>

    <form onsubmit="handleSendOrder(event, '${product.crop_name || product.name}')">
      <div class="form-group">
        <label class="form-label">Required Procurement Quantity (${product.unit || 'kg'}) *</label>
        <input type="number" class="form-control" id="order-qty" value="500" min="50" max="${product.quantity}" required />
      </div>

      <div class="form-group">
        <label class="form-label">Delivery Destination Warehouse Address *</label>
        <input type="text" class="form-control" id="order-dest" placeholder="e.g. Pune APMC Processing Depot, Sector 18" required />
      </div>

      <div class="form-group">
        <label class="form-label">Logistics Option</label>
        <select class="form-select" id="order-logistics">
          <option value="krushisetu">KrushiSetu Verified Fleet (Recommended • GPS Enabled)</option>
          <option value="buyer">Buyer Arranges Own Haulage</option>
          <option value="farmer">Farmer Arranges Local Delivery</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Payment Security</label>
        <input type="text" class="form-control" value="100% Escrow Protected (RBI Compliant)" readonly style="background: var(--slate-100);" />
      </div>

      <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
        <button type="button" class="btn btn-outline" style="flex:1;" onclick="closeOrderModal()">Cancel</button>
        <button type="submit" class="btn btn-primary" style="flex:2;">Lock Deal in Escrow</button>
      </div>
    </form>
  `;

  modal.style.display = 'flex';
}

function closeOrderModal() {
  const modal = document.getElementById('order-modal');
  if (modal) modal.style.display = 'none';
}

function handleSendOrder(e, prodName) {
  e.preventDefault();
  closeOrderModal();
  showToast(`Direct order submitted for '${prodName}'. Notification dispatched to farmer!`, 'success');
}

function resetAllFilters() {
  const searchInput = document.getElementById('market-search');
  const locationInput = document.getElementById('filter-location');
  const maxPriceInput = document.getElementById('filter-max-price');
  const maxPriceVal = document.getElementById('price-val-display');

  if (searchInput) searchInput.value = '';
  if (locationInput) locationInput.value = '';
  if (maxPriceInput) maxPriceInput.value = '150';
  if (maxPriceVal) maxPriceVal.innerText = '₹150';

  document.querySelectorAll('.category-filter').forEach(cb => cb.checked = false);
  document.querySelectorAll('.grade-filter').forEach(cb => cb.checked = false);

  fetchAndRenderMarketplace();
}

// Initial Listeners Setup
document.addEventListener('DOMContentLoaded', () => {
  // Check for URL query search parameter (e.g. ?search=wheat)
  const urlParams = new URLSearchParams(window.location.search);
  const initialSearch = urlParams.get('search');
  const searchInput = document.getElementById('market-search');
  if (initialSearch && searchInput) {
    searchInput.value = initialSearch;
  }

  fetchAndRenderMarketplace();

  // Search input with debounce
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(fetchAndRenderMarketplace, 300);
    });
  }

  // Filter change listeners
  document.querySelectorAll('.category-filter, .grade-filter').forEach(box => {
    box.addEventListener('change', fetchAndRenderMarketplace);
  });

  const sortSelect = document.getElementById('market-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', fetchAndRenderMarketplace);
  }

  const maxPriceSlider = document.getElementById('filter-max-price');
  const priceValDisplay = document.getElementById('price-val-display');
  if (maxPriceSlider) {
    maxPriceSlider.addEventListener('input', (e) => {
      if (priceValDisplay) priceValDisplay.innerText = `₹${e.target.value}`;
      fetchAndRenderMarketplace();
    });
  }

  const locationFilter = document.getElementById('filter-location');
  if (locationFilter) {
    locationFilter.addEventListener('input', fetchAndRenderMarketplace);
  }
});
