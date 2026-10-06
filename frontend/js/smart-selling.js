/**
 * KrushiSetu Smart Selling Decision Support & Transportation Estimator Client
 * Core Formula: Expected Net Realization = Expected Revenue - Transportation Cost - Other Selling Costs
 * Decision Support Tool: The farmer retains 100% final authority.
 */

async function recalculateSmartSelling() {
  const cropEl = document.getElementById('calc-crop');
  const qtyEl = document.getElementById('calc-quantity');
  const gradeEl = document.getElementById('calc-grade');
  const originEl = document.getElementById('calc-origin');

  const crop = cropEl ? cropEl.value : 'Tomato';
  const qty = parseFloat(qtyEl ? qtyEl.value : 500) || 500;
  const grade = gradeEl ? gradeEl.value : 'Grade A+';
  const origin = originEl ? originEl.value : 'Nashik';

  const badgeEl = document.getElementById('table-crop-badge');
  if (badgeEl) {
    badgeEl.textContent = `${crop} • ${qty.toLocaleString()} kg • ${grade}`;
  }

  try {
    const res = await fetch('/api/smart-selling/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop: crop,
        quantity_kg: qty,
        quality: grade,
        farmer_location: origin
      })
    });

    const data = await res.json();
    if (data && data.success && data.comparisons) {
      renderComparisonCards(data.comparisons, qty, crop);
      renderComparisonTable(data.comparisons);
      renderWhyFactors(data.comparisons);
    }
  } catch (err) {
    console.error('Failed to recalculate smart selling:', err);
  }
}

function renderComparisonCards(results, qty, crop) {
  const container = document.getElementById('smart-selling-cards');
  if (!container) return;

  container.innerHTML = results.map(item => {
    const isRecommended = item.is_recommended;
    const priceDisplay = item.expected_price_range ? item.expected_price_range.display : 'Market Range';
    return `
      <div class="buyer-offer-card ${isRecommended ? 'recommended' : ''}">
        ${isRecommended ? '<div class="recommended-ribbon">⭐ Highest Net In-Pocket Profit</div>' : ''}
        
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 0.75rem;">
          <div>
            <h3 style="font-size: 1.15rem; color: var(--slate-900);">${item.buyer_name}</h3>
            <span class="badge ${isRecommended ? 'badge-success' : 'badge-earth'}" style="margin-top: 0.35rem;">
              ${item.buyer_badge || 'Verified Commercial Buyer'}
            </span>
          </div>
        </div>

        <p style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 0.85rem;">
          📍 ${item.location} (<strong>${item.distance_km} km haul</strong>) | 💳 <strong>${item.payment_terms}</strong>
        </p>

        <div style="background: var(--slate-50); padding: 0.85rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
          <div style="display:flex; justify-content:space-between; font-size: 0.88rem;">
            <span>Nominal Bid Rate:</span>
            <strong style="color: ${item.offered_price_per_kg >= 35 ? 'var(--primary-700)' : 'var(--slate-800)'}">
              ₹${item.offered_price_per_kg.toFixed(2)} / kg
            </strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size: 0.88rem; margin-top: 0.25rem;">
            <span>Gross Revenue (${qty.toLocaleString()} kg):</span>
            <strong>₹${Math.round(item.expected_revenue).toLocaleString('en-IN')}</strong>
          </div>
        </div>

        <!-- Expense Deductions Breakdown -->
        <div style="margin-bottom: 1rem;">
          <div class="breakdown-row">
            <span style="color: var(--danger);">(-) Transportation Freight:</span>
            <span style="font-weight:600; color: var(--danger);">₹${Math.round(item.transport_cost).toLocaleString('en-IN')}</span>
          </div>
          <div class="breakdown-row">
            <span style="color: var(--danger);">(-) Packaging & Other Selling Costs:</span>
            <span>₹${Math.round(item.other_costs).toLocaleString('en-IN')}</span>
          </div>
          
          <div class="breakdown-row net-realization">
            <span>Expected Net Realization:</span>
            <span style="color: ${isRecommended ? 'var(--primary-700)' : 'var(--slate-800)'}">
              ₹${Math.round(item.net_realization).toLocaleString('en-IN')}
            </span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; margin-top: 0.35rem;">
            <span style="color: var(--slate-500);">Expected Range: ${priceDisplay}</span>
            <span style="color: var(--primary-700); font-weight:700;">In-Pocket: ₹${item.net_rate_per_kg.toFixed(2)}/kg</span>
          </div>
        </div>

        <div style="margin-top: auto; padding-top: 0.75rem;">
          <button class="btn ${isRecommended ? 'btn-primary' : 'btn-outline'} btn-sm" style="width: 100%; font-weight: 700;" onclick="acceptSmartOffer('${item.buyer_name}', ${Math.round(item.net_realization)})">
            ${isRecommended ? '🚀 Select This Smart Selling Opportunity' : 'Select This Buyer'}
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderComparisonTable(results) {
  const tbody = document.getElementById('smart-selling-table-body');
  if (!tbody) return;

  tbody.innerHTML = results.map(r => {
    const isRec = r.is_recommended;
    const priceRangeText = r.expected_price_range ? r.expected_price_range.display : '₹27–₹31/kg';
    return `
      <tr style="${isRec ? 'background: rgba(34, 197, 94, 0.05); font-weight: 500;' : ''}">
        <td>
          <strong>${r.buyer_name}</strong>
          ${isRec ? '<span class="badge badge-success" style="font-size: 0.7rem; margin-left: 0.35rem;">Best Net Profit</span>' : ''}
        </td>
        <td>${r.location}</td>
        <td>${r.crop} (${r.quality || 'Grade A'})</td>
        <td>${r.quantity_kg.toLocaleString()} kg</td>
        <td><strong>₹${r.offered_price_per_kg.toFixed(2)}</strong></td>
        <td>${r.distance_km} km</td>
        <td style="color: var(--danger);">₹${Math.round(r.transport_cost).toLocaleString('en-IN')}</td>
        <td style="color: var(--danger);">₹${Math.round(r.other_costs).toLocaleString('en-IN')}</td>
        <td><strong>₹${Math.round(r.expected_revenue).toLocaleString('en-IN')}</strong></td>
        <td><strong style="color: ${isRec ? 'var(--primary-700)' : 'var(--slate-900)'}; font-size: 1.05rem;">₹${Math.round(r.net_realization).toLocaleString('en-IN')}</strong></td>
        <td><span class="badge badge-primary">${r.demand_trend || 'Stable'}</span></td>
        <td><small style="color: var(--slate-600);">${priceRangeText}</small></td>
      </tr>
    `;
  }).join('');
}

function renderWhyFactors(results) {
  const container = document.getElementById('why-factors-container');
  if (!container || !results || results.length === 0) return;

  const topOffer = results[0];
  const factors = topOffer.why_this_estimate || [];

  if (factors.length > 0) {
    container.innerHTML = factors.map(f => `
      <div style="background: var(--slate-50); padding: 0.65rem 0.85rem; border-radius: var(--radius-md); border-left: 3px solid var(--primary-600);">
        <strong>💡 Key Factor:</strong> ${f}
      </div>
    `).join('');
  }
}

function acceptSmartOffer(buyerName, netAmount) {
  if (typeof showToast === 'function') {
    showToast(`Decision selected: Proceeding with ${buyerName} for Net ₹${netAmount.toLocaleString('en-IN')}!`, 'success');
  } else {
    alert(`Decision selected: Proceeding with ${buyerName} for Net ₹${netAmount.toLocaleString('en-IN')}!`);
  }
}

/**
 * Real-time Transportation Cost Estimation Integration
 */
async function calculateTransportEstimate() {
  const originEl = document.getElementById('t-origin');
  const destEl = document.getElementById('t-destination');
  const qtyEl = document.getElementById('t-quantity');
  const vehicleEl = document.getElementById('t-vehicle');
  const coldChainEl = document.getElementById('t-cold-chain');

  const origin = originEl ? originEl.value : 'Nashik';
  const destination = destEl ? destEl.value : 'Mumbai';
  const quantityKg = parseFloat(qtyEl ? qtyEl.value : 500) || 500;
  const vehicleType = vehicleEl ? vehicleEl.value : '';
  const requiresColdStorage = coldChainEl ? coldChainEl.checked : false;

  const payload = {
    farmer_location: origin,
    buyer_location: destination,
    quantity_kg: quantityKg,
    vehicle_type: vehicleType,
    requires_cold_storage: requiresColdStorage
  };

  try {
    const res = await fetch('/api/smart-selling/transport-estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data && data.success) {
      const resultBox = document.getElementById('transport-result');
      if (resultBox) resultBox.style.display = 'block';

      document.getElementById('res-distance').textContent = `${data.distance_km} km`;
      document.getElementById('res-transit').textContent = `~${data.transit_hours} hrs transit`;
      document.getElementById('res-vehicle').textContent = data.vehicle_type.name;
      document.getElementById('res-trips').textContent = `${data.trips_required} trip${data.trips_required > 1 ? 's' : ''} required`;
      document.getElementById('res-rate-kg').textContent = `₹${data.cost_breakdown.effective_cost_per_kg.toFixed(2)} / kg`;
      document.getElementById('res-rate-qtl').textContent = `₹${data.cost_breakdown.effective_cost_per_quintal.toFixed(2)} / quintal`;
      document.getElementById('res-total-cost').textContent = `₹${data.cost_breakdown.total_estimated_transport_cost.toLocaleString('en-IN')}`;

      document.getElementById('res-base-freight').textContent = `₹${data.cost_breakdown.base_freight.toLocaleString('en-IN')}`;
      document.getElementById('res-handling').textContent = `₹${data.cost_breakdown.handling_and_loading.toLocaleString('en-IN')}`;
      document.getElementById('res-toll').textContent = `₹${data.cost_breakdown.toll_and_permits.toLocaleString('en-IN')}`;
      document.getElementById('res-cooling').textContent = `₹${data.cost_breakdown.cold_storage_surcharge.toLocaleString('en-IN')}`;
    }
  } catch (err) {
    console.error('Failed to estimate transport:', err);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  recalculateSmartSelling();
  calculateTransportEstimate();
});
