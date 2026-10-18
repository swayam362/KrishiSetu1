/**
 * KrushiSetu Owner/Admin Dashboard Controller
 * Connects directly to protected backend /api/admin/* endpoints
 */

const AdminController = {
  activeTab: 'overview',
  farmersPage: 1,
  buyersPage: 1,
  productsPage: 1,
  ordersPage: 1,

  async init() {
    // 1. Enforce strict client-side role check
    const token = API.getToken();
    if (!token) {
      window.location.href = 'login.html?unauthorized=1';
      return;
    }

    try {
      const profileRes = await API.getProfile();
      if (!profileRes.user || profileRes.user.role !== 'admin') {
        showToast('Access denied: Administrator privileges required.', 'error');
        setTimeout(() => { window.location.href = 'login.html?unauthorized=1'; }, 800);
        return;
      }

      const adminUser = profileRes.user;
      document.getElementById('admin-name-display').innerText = adminUser.full_name || 'Admin';
      document.getElementById('admin-email-display').innerText = adminUser.email || '';
    } catch (e) {
      window.location.href = 'login.html?expired=1';
      return;
    }

    // 2. Setup tab navigation
    this.setupTabs();

    // 3. Load Overview by default
    await this.loadOverview();
  },

  setupTabs() {
    const tabBtns = document.querySelectorAll('.admin-nav-item');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = btn.getAttribute('data-tab');
        if (!tab) return;
        this.switchTab(tab);
      });
    });
  },

  switchTab(tabName) {
    this.activeTab = tabName;

    // Update nav classes
    document.querySelectorAll('.admin-nav-item').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-tab') === tabName);
    });

    // Update section visibility
    document.querySelectorAll('.admin-tab-pane').forEach(p => {
      p.style.display = p.id === `tab-${tabName}` ? 'block' : 'none';
    });

    // Lazy load tab data
    if (tabName === 'overview') this.loadOverview();
    else if (tabName === 'farmers') this.loadFarmers();
    else if (tabName === 'buyers') this.loadBuyers();
    else if (tabName === 'products') this.loadProducts();
    else if (tabName === 'orders') this.loadOrders();
    else if (tabName === 'monitoring') this.loadMonitoring();
  },

  // =========================================================================
  // A. OVERVIEW
  // =========================================================================
  async loadOverview() {
    try {
      const res = await API.request('/api/admin/overview');
      if (!res.success) throw new Error(res.error || 'Failed to fetch overview metrics');

      const m = res.metrics;
      document.getElementById('stat-farmers').innerText = (m.total_farmers || 0).toLocaleString();
      document.getElementById('stat-buyers').innerText = (m.total_buyers || 0).toLocaleString();
      document.getElementById('stat-products').innerText = (m.total_products || 0).toLocaleString();
      document.getElementById('stat-orders').innerText = (m.total_orders || 0).toLocaleString();
      document.getElementById('stat-pending-orders').innerText = (m.pending_orders || 0).toLocaleString();
      document.getElementById('stat-completed-orders').innerText = (m.completed_orders || 0).toLocaleString();
      document.getElementById('stat-volume-settled').innerText = `₹${(m.settled_volume_inr || 0).toLocaleString('en-IN')}`;

      // Recent Activity
      const activityContainer = document.getElementById('recent-activity-list');
      if (res.recent_activity && res.recent_activity.length > 0) {
        activityContainer.innerHTML = res.recent_activity.map(item => `
          <div class="activity-timeline-item">
            <div class="activity-icon-badge">${this.getActivityIcon(item.action)}</div>
            <div style="flex: 1;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <strong style="color: var(--slate-900); font-size: 0.9rem;">${item.action.replace(/_/g, ' ')}</strong>
                <span style="font-size: 0.75rem; color: var(--slate-400);">${this.formatDate(item.created_at)}</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--slate-600); margin-top: 0.2rem;">${item.details || item.target_id}</p>
              <small style="font-size: 0.75rem; color: var(--slate-400);">Admin: ${item.admin_email || 'System'}</small>
            </div>
          </div>
        `).join('');
      } else {
        activityContainer.innerHTML = `<div style="text-align: center; color: var(--slate-400); padding: 2rem;">No recent administrative activity logged yet.</div>`;
      }

    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // =========================================================================
  // B. FARMER MANAGEMENT
  // =========================================================================
  async loadFarmers() {
    const search = document.getElementById('search-farmers')?.value.trim() || '';
    const status = document.getElementById('filter-farmer-status')?.value || 'all';
    const tbody = document.getElementById('farmers-table-body');
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem;">Loading farmers from database...</td></tr>`;

    try {
      const q = new URLSearchParams({ search, status, page: this.farmersPage, limit: 15 });
      const res = await API.request(`/api/admin/farmers?${q.toString()}`);
      if (!res.success) throw new Error(res.error || 'Failed to fetch farmers');

      document.getElementById('badge-farmers-count').innerText = `${res.total} Registered`;

      if (res.farmers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--slate-500);">No farmer records found matching filter.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.farmers.map(f => `
        <tr>
          <td><code style="font-size: 0.78rem; background: var(--slate-100); padding: 0.2rem 0.4rem; border-radius: 4px;">${f.id.substring(0, 8)}...</code></td>
          <td>
            <strong>${f.full_name}</strong>
            <div style="font-size: 0.75rem; color: var(--slate-500);">Crops: ${f.primary_crops || 'General'}</div>
          </td>
          <td>
            <div>✉️ ${f.email}</div>
            <div style="font-size: 0.78rem; color: var(--slate-500);">📞 ${f.phone || 'N/A'}</div>
          </td>
          <td>${f.district || f.village || 'N/A'}, ${f.state || 'MH'}</td>
          <td>${f.farm_size_acres ? `${f.farm_size_acres} Acres` : 'N/A'}</td>
          <td><small style="color: var(--slate-500);">${this.formatDate(f.created_at)}</small></td>
          <td>
            <span class="badge ${f.is_active ? 'badge-success' : 'badge-danger'}">
              ${f.is_active ? 'Active' : 'Inactive'}
            </span>
          </td>
          <td>
            <button class="btn ${f.is_active ? 'btn-outline-danger' : 'btn-outline-primary'} btn-sm"
              onclick="AdminController.toggleUserStatus('${f.id}', ${!f.is_active}, 'farmer')">
              ${f.is_active ? 'Deactivate' : 'Activate'}
            </button>
          </td>
        </tr>
      `).join('');

      this.renderPagination('farmers', res.total, this.farmersPage, 15);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" style="color: var(--danger); text-align: center; padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  // =========================================================================
  // C. BUYER / MERCHANT MANAGEMENT
  // =========================================================================
  async loadBuyers() {
    const search = document.getElementById('search-buyers')?.value.trim() || '';
    const status = document.getElementById('filter-buyer-status')?.value || 'all';
    const tbody = document.getElementById('buyers-table-body');
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem;">Loading bulk buyers from database...</td></tr>`;

    try {
      const q = new URLSearchParams({ search, status, page: this.buyersPage, limit: 15 });
      const res = await API.request(`/api/admin/buyers?${q.toString()}`);
      if (!res.success) throw new Error(res.error || 'Failed to fetch buyers');

      document.getElementById('badge-buyers-count').innerText = `${res.total} Registered`;

      if (res.buyers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--slate-500);">No buyer records found matching filter.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.buyers.map(b => `
        <tr>
          <td><code style="font-size: 0.78rem; background: var(--slate-100); padding: 0.2rem 0.4rem; border-radius: 4px;">${b.id.substring(0, 8)}...</code></td>
          <td>
            <strong>${b.full_name}</strong>
            <div style="font-size: 0.8rem; color: var(--primary-700); font-weight: 600;">${b.business_name || 'Individual Merchant'}</div>
          </td>
          <td>
            <div>✉️ ${b.email}</div>
            <div style="font-size: 0.78rem; color: var(--slate-500);">📞 ${b.phone || 'N/A'}</div>
          </td>
          <td>${b.city || b.district || 'N/A'}, ${b.state || 'MH'}</td>
          <td><code style="font-size: 0.75rem;">${b.gstin || 'Unregistered'}</code></td>
          <td><small style="color: var(--slate-500);">${this.formatDate(b.created_at)}</small></td>
          <td>
            <span class="badge ${b.is_active ? 'badge-success' : 'badge-danger'}">
              ${b.is_active ? 'Active' : 'Inactive'}
            </span>
          </td>
          <td>
            <button class="btn ${b.is_active ? 'btn-outline-danger' : 'btn-outline-primary'} btn-sm"
              onclick="AdminController.toggleUserStatus('${b.id}', ${!b.is_active}, 'buyer')">
              ${b.is_active ? 'Deactivate' : 'Activate'}
            </button>
          </td>
        </tr>
      `).join('');

      this.renderPagination('buyers', res.total, this.buyersPage, 15);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" style="color: var(--danger); text-align: center; padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  async toggleUserStatus(userId, newStatus, roleType) {
    const actionWord = newStatus ? 'activate' : 'deactivate';
    if (!confirm(`Are you sure you want to ${actionWord} this ${roleType} account?`)) return;

    try {
      const res = await API.request(`/api/admin/users/${userId}/status`, {
        method: 'PATCH',
        body: { is_active: newStatus }
      });
      showToast(res.message, 'success');
      if (roleType === 'farmer') this.loadFarmers();
      else this.loadBuyers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // =========================================================================
  // D. PRODUCT MANAGEMENT
  // =========================================================================
  async loadProducts() {
    const search = document.getElementById('search-products')?.value.trim() || '';
    const category = document.getElementById('filter-product-category')?.value || 'all';
    const availability = document.getElementById('filter-product-avail')?.value || 'all';
    const tbody = document.getElementById('products-table-body');
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem;">Loading produce listings...</td></tr>`;

    try {
      const q = new URLSearchParams({ search, category, availability, page: this.productsPage, limit: 15 });
      const res = await API.request(`/api/admin/products?${q.toString()}`);
      if (!res.success) throw new Error(res.error || 'Failed to fetch products');

      document.getElementById('badge-products-count').innerText = `${res.total} Lots`;

      if (res.products.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--slate-500);">No produce listings matching filter.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.products.map(p => `
        <tr>
          <td><code style="font-size: 0.78rem; background: var(--slate-100); padding: 0.2rem 0.4rem; border-radius: 4px;">${p.id.substring(0, 8)}...</code></td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.65rem;">
              <img src="${p.image_url || p.images?.[0] || 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=80&q=80'}"
                   style="width: 36px; height: 36px; border-radius: 6px; object-fit: cover;" />
              <div>
                <strong>${p.crop_name || p.name}</strong>
                <div style="font-size: 0.75rem; color: var(--slate-500);">Farmer: ${p.farmer_name}</div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-earth">${p.category || 'Grains'}</span></td>
          <td><strong>${(p.quantity || 0).toLocaleString()}</strong> ${p.unit || 'kg'}</td>
          <td><strong style="color: var(--primary-800);">₹${(p.price_per_unit || p.price || 0).toFixed(2)}</strong></td>
          <td>${p.location || `${p.district || ''}, ${p.state || ''}`}</td>
          <td>
            <span class="badge ${p.availability === 'Available' ? 'badge-success' : (p.availability === 'Deactivated' ? 'badge-danger' : 'badge-warning')}">
              ${p.availability}
            </span>
          </td>
          <td>
            <div style="display: flex; gap: 0.35rem;">
              <button class="btn btn-outline btn-sm" title="Toggle Active / Deactivate"
                onclick="AdminController.toggleProductAvailability('${p.id}', '${p.availability === 'Available' ? 'Deactivated' : 'Available'}')">
                ${p.availability === 'Available' ? '🚫 Deactivate' : '✔️ Restore'}
              </button>
              <button class="btn btn-outline-danger btn-sm" title="Delete Listing"
                onclick="AdminController.deleteProduct('${p.id}', '${p.crop_name || p.name}')">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      `).join('');

      this.renderPagination('products', res.total, this.productsPage, 15);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" style="color: var(--danger); text-align: center; padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  async toggleProductAvailability(prodId, newAvail) {
    try {
      const res = await API.request(`/api/admin/products/${prodId}/availability`, {
        method: 'PATCH',
        body: { availability: newAvail }
      });
      showToast(res.message, 'success');
      this.loadProducts();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async deleteProduct(prodId, cropName) {
    if (!confirm(`Are you sure you want to permanently remove listing '${cropName}'?`)) return;

    try {
      const res = await API.request(`/api/admin/products/${prodId}`, {
        method: 'DELETE'
      });
      showToast(res.message, 'success');
      this.loadProducts();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // =========================================================================
  // E. ORDER MANAGEMENT
  // =========================================================================
  async loadOrders() {
    const search = document.getElementById('search-orders')?.value.trim() || '';
    const status = document.getElementById('filter-order-status')?.value || 'all';
    const tbody = document.getElementById('orders-table-body');
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem;">Loading order transactions...</td></tr>`;

    try {
      const q = new URLSearchParams({ search, status, page: this.ordersPage, limit: 15 });
      const res = await API.request(`/api/admin/orders?${q.toString()}`);
      if (!res.success) throw new Error(res.error || 'Failed to fetch orders');

      document.getElementById('badge-orders-count').innerText = `${res.total} Orders`;

      if (res.orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--slate-500);">No orders found matching criteria.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.orders.map(o => `
        <tr>
          <td><code style="font-weight: 700; color: var(--primary-900);">${o.id}</code></td>
          <td>
            <strong>${o.product_name}</strong>
            <div style="font-size: 0.75rem; color: var(--slate-500);">${o.quantity} ${o.unit}</div>
          </td>
          <td>
            <div>🏢 ${o.buyer_name}</div>
            <small style="color: var(--slate-500);">Farmer: ${o.farmer_name}</small>
          </td>
          <td><strong style="color: var(--primary-900); font-size: 1rem;">₹${(o.total_amount || 0).toLocaleString('en-IN')}</strong></td>
          <td><small style="color: var(--slate-600);">${o.delivery_address || 'Wholesale Depot'}</small></td>
          <td>
            <span class="badge ${this.getOrderBadgeClass(o.status)}">${o.status}</span>
            <div style="font-size: 0.72rem; color: var(--slate-500); margin-top: 0.2rem;">${o.escrow_status ? '🔒 ' + o.escrow_status.substring(0, 22) + '...' : ''}</div>
          </td>
          <td><small style="color: var(--slate-500);">${this.formatDate(o.created_at)}</small></td>
          <td>
            <select class="form-control" style="font-size: 0.78rem; padding: 0.25rem 0.5rem; width: auto;"
              onchange="AdminController.overrideOrderStatus('${o.id}', this.value)">
              <option value="" disabled selected>Change Status</option>
              <option value="Pending">Pending</option>
              <option value="Accepted">Accepted</option>
              <option value="Processing">Processing</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </td>
        </tr>
      `).join('');

      this.renderPagination('orders', res.total, this.ordersPage, 15);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" style="color: var(--danger); text-align: center; padding: 2rem;">Error: ${err.message}</td></tr>`;
    }
  },

  async overrideOrderStatus(orderId, newStatus) {
    if (!newStatus) return;
    if (!confirm(`Confirm administrative transition of order ${orderId} to '${newStatus}'?`)) {
      this.loadOrders();
      return;
    }

    try {
      const res = await API.request(`/api/admin/orders/${orderId}/status`, {
        method: 'PATCH',
        body: { status: newStatus }
      });
      showToast(res.message, 'success');
      this.loadOrders();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // =========================================================================
  // F. AI & SYSTEM MONITORING
  // =========================================================================
  async loadMonitoring() {
    try {
      const res = await API.request('/api/admin/system-monitoring');
      if (!res.success) throw new Error(res.error || 'Failed to fetch monitoring telemetry');

      const ai = res.ai_metrics || {};
      document.getElementById('mon-disease-count').innerText = (ai.disease_diagnoses_count || 0).toLocaleString();
      document.getElementById('mon-soil-count').innerText = (ai.soil_health_analyses_count || 0).toLocaleString();
      document.getElementById('mon-pred-count').innerText = (ai.market_price_predictions_count || 0).toLocaleString();

      // Database Health
      const db = res.database || {};
      const dbStatusEl = document.getElementById('mon-db-status');
      if (db.healthy) {
        dbStatusEl.innerHTML = `<span style="color: var(--primary-500); font-weight: 700;">🟢 Connected & Responsive</span>`;
      } else {
        dbStatusEl.innerHTML = `<span style="color: var(--danger); font-weight: 700;">🔴 Disconnected / Degraded</span>`;
      }

      // Collections Table
      const colTbody = document.getElementById('mon-collections-body');
      if (db.collection_counts) {
        colTbody.innerHTML = Object.entries(db.collection_counts).map(([name, count]) => `
          <tr>
            <td><code>${name}</code></td>
            <td style="text-align: right;"><strong>${count.toLocaleString()}</strong> records</td>
          </tr>
        `).join('');
      }

      // Security Audit Log Table
      const logTbody = document.getElementById('mon-audit-log-body');
      if (res.recent_system_events && res.recent_system_events.length > 0) {
        logTbody.innerHTML = res.recent_system_events.map(ev => `
          <tr>
            <td><span class="badge badge-earth">${ev.action}</span></td>
            <td>${ev.admin_email || 'System'}</td>
            <td><code>${ev.target_type || 'SYS'}:${ev.target_id || ''}</code></td>
            <td><small>${ev.details || '-'}</small></td>
            <td><small style="color: var(--slate-400);">${this.formatDate(ev.created_at)}</small></td>
          </tr>
        `).join('');
      } else {
        logTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--slate-400);">No administrative audit events recorded yet.</td></tr>`;
      }

    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // =========================================================================
  // UTILITIES
  // =========================================================================
  formatDate(isoStr) {
    if (!isoStr) return '-';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-IN', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoStr.substring(0, 10);
    }
  },

  getActivityIcon(action) {
    if (!action) return '⚡';
    if (action.includes('USER')) return '👤';
    if (action.includes('PRODUCT')) return '🌾';
    if (action.includes('ORDER')) return '📦';
    if (action.includes('LOGIN')) return '🔐';
    return '⚡';
  },

  getOrderBadgeClass(status) {
    if (status === 'Delivered' || status === 'Completed') return 'badge-success';
    if (status === 'Pending') return 'badge-warning';
    if (status === 'Shipped') return 'badge-info';
    if (status === 'Accepted' || status === 'Processing') return 'badge-earth';
    if (status === 'Cancelled' || status === 'Rejected') return 'badge-danger';
    return 'badge-earth';
  },

  renderPagination(type, total, currentPage, limit) {
    const totalPages = Math.ceil(total / limit) || 1;
    const container = document.getElementById(`pagination-${type}`);
    if (!container) return;

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; font-size: 0.88rem; color: var(--slate-500);">
        <div>Showing page ${currentPage} of ${totalPages} (${total} total records)</div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-outline btn-sm" ${currentPage <= 1 ? 'disabled' : ''}
            onclick="AdminController.changePage('${type}', ${currentPage - 1})">
            ← Previous
          </button>
          <button class="btn btn-outline btn-sm" ${currentPage >= totalPages ? 'disabled' : ''}
            onclick="AdminController.changePage('${type}', ${currentPage + 1})">
            Next →
          </button>
        </div>
      </div>
    `;
  },

  changePage(type, newPage) {
    if (type === 'farmers') { this.farmersPage = newPage; this.loadFarmers(); }
    else if (type === 'buyers') { this.buyersPage = newPage; this.loadBuyers(); }
    else if (type === 'products') { this.productsPage = newPage; this.loadProducts(); }
    else if (type === 'orders') { this.ordersPage = newPage; this.loadOrders(); }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AdminController.init();
});
