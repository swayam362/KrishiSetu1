/**
 * KrushiSetu Market Intelligence & Demand Prediction Client
 * Interfaces with backend XGBoost ML endpoints, renders time-series forecasts,
 * plots uncertainty envelopes, and breaks down driving agro-economic factors.
 */

let forecastChartInstance = null;

async function fetchAndRenderForecast() {
  const cropSelect = document.getElementById('market-crop-select');
  const locationSelect = document.getElementById('market-location-select');
  const horizonSelect = document.getElementById('market-horizon-select');

  const crop = cropSelect ? cropSelect.value : 'Tomato';
  const location = locationSelect ? locationSelect.value : 'Pune';
  const period = horizonSelect ? horizonSelect.value : 'Next 7 days';

  const loadingEl = document.getElementById('forecast-loading');
  const contentEl = document.getElementById('forecast-content');

  if (loadingEl) loadingEl.style.display = 'block';
  if (contentEl) contentEl.style.opacity = '0.4';

  try {
    const response = await fetch(`/api/ai/market-intelligence/forecast?crop=${encodeURIComponent(crop)}&location=${encodeURIComponent(location)}&period=${encodeURIComponent(period)}`);
    const data = await response.json();

    if (data && data.success) {
      updateDashboardUI(data);
    } else {
      console.error('Forecast API error:', data);
    }
  } catch (error) {
    console.error('Failed to fetch market forecast:', error);
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.opacity = '1';
  }
}

function updateDashboardUI(data) {
  // 1. Demand Level Badge
  const demandLevelEl = document.getElementById('kpi-demand-level');
  if (demandLevelEl) {
    const lvl = (data.current_demand_level || 'Moderate').toLowerCase();
    let pillClass = 'moderate';
    if (lvl.includes('very high')) pillClass = 'very-high';
    else if (lvl.includes('high')) pillClass = 'high';
    else if (lvl.includes('low')) pillClass = 'low';

    demandLevelEl.innerHTML = `<span class="demand-pill ${pillClass}">${data.current_demand_level}</span>`;
  }

  // 2. Trend text
  const demandTrendEl = document.getElementById('kpi-demand-trend');
  if (demandTrendEl) {
    demandTrendEl.textContent = data.predicted_trend || 'Demand stable';
    demandTrendEl.style.color = (data.trend_direction === 'surge' || data.trend_direction === 'up') ? 'var(--primary-700)' : '#475569';
  }

  // 3. Current Price
  const currentPriceEl = document.getElementById('kpi-current-price');
  if (currentPriceEl) {
    currentPriceEl.textContent = Number(data.current_modal_price || 0).toFixed(2);
  }

  const locSubEl = document.getElementById('kpi-location-sub');
  if (locSubEl) {
    locSubEl.textContent = `${data.location} Benchmark`;
  }

  // 4. Projected Price & Change
  const projectedPriceEl = document.getElementById('kpi-projected-price');
  if (projectedPriceEl) {
    projectedPriceEl.textContent = Number(data.projected_price || 0).toFixed(2);
  }

  const priceChangeEl = document.getElementById('kpi-price-change');
  if (priceChangeEl) {
    const chg = data.price_change_percent || 0;
    const sign = chg >= 0 ? '▲ +' : '▼ ';
    priceChangeEl.textContent = `${sign}${chg}% Projected Change`;
    priceChangeEl.style.color = chg >= 0 ? 'var(--primary-700)' : 'var(--danger)';
  }

  // 5. Confidence & Uncertainty
  const confEl = document.getElementById('kpi-confidence');
  if (confEl) {
    confEl.textContent = `${data.confidence_percent || 90}%`;
  }

  const uncEl = document.getElementById('kpi-uncertainty');
  if (uncEl && data.uncertainty) {
    uncEl.textContent = data.uncertainty.range_text || '± ₹2.00 / kg';
  }

  // 6. Action Advisory
  const advisoryTextEl = document.getElementById('advisory-text');
  if (advisoryTextEl) {
    advisoryTextEl.textContent = data.action_advisory || 'Maintain balanced marketing strategy.';
  }

  const horizonBadgeEl = document.getElementById('advisory-horizon-badge');
  if (horizonBadgeEl) {
    horizonBadgeEl.textContent = `${data.forecast_period} Forecast`;
  }

  // 7. Important Driving Factors
  const factorsContainer = document.getElementById('factors-list');
  if (factorsContainer && data.important_factors) {
    factorsContainer.innerHTML = data.important_factors.map(f => `
      <div class="factor-item ${f.type || 'neutral'}">
        <span class="factor-category">${f.category || 'Economic Indicator'}</span>
        <div class="factor-title">${f.factor}</div>
        <div class="factor-impact">${f.impact}</div>
      </div>
    `).join('');
  }

  // 8. Weather & Supply Context
  if (data.weather_summary) {
    const tempEl = document.getElementById('weather-temp');
    const condEl = document.getElementById('weather-condition');
    const rainEl = document.getElementById('weather-rain');
    const humEl = document.getElementById('weather-humidity');

    if (tempEl) tempEl.textContent = `${data.weather_summary.temperature_c}°C`;
    if (condEl) condEl.textContent = data.weather_summary.condition;
    if (rainEl) rainEl.textContent = `${data.weather_summary.rainfall_mm} mm`;
    if (humEl) humEl.textContent = `Humidity: ${data.weather_summary.humidity_percent}%`;
  }

  if (data.market_supply_summary) {
    const arrivalsEl = document.getElementById('mandi-arrivals');
    const seasonEl = document.getElementById('crop-season');
    if (arrivalsEl) arrivalsEl.textContent = `${Number(data.market_supply_summary.market_arrivals_quintals).toLocaleString()} Qtl`;
    if (seasonEl) seasonEl.textContent = data.market_supply_summary.season || 'Current Season';
  }

  // 9. Update Live Mandi Comparison Rows
  updateMandiComparisonTable(data.crop, data.current_modal_price);

  // 10. Render Time-Series Chart with Uncertainty Envelope
  renderForecastChart(data.chart_data, data.crop);
}

function updateMandiComparisonTable(crop, basePrice) {
  const tableBody = document.getElementById('mandi-comparison-rows');
  if (!tableBody) return;

  const mandis = [
    { name: "Lasalgaon Mandi", state: "Maharashtra", multiplier: 1.02, arrival: "14,200 Quintals", trend: "+2.1%", trendColor: "var(--primary-700)" },
    { name: "Nashik Main Yard", state: "Maharashtra", multiplier: 1.00, arrival: "9,800 Quintals", trend: "0.0%", trendColor: "var(--slate-500)" },
    { name: "Indore APMC", state: "Madhya Pradesh", multiplier: 0.97, arrival: "16,400 Quintals", trend: "-1.2%", trendColor: "var(--danger)" },
    { name: "Vashi APMC (Navi Mumbai)", state: "Maharashtra", multiplier: 1.09, arrival: "6,500 Quintals", trend: "+3.8%", trendColor: "var(--primary-700)" },
    { name: "Guntur Market Yard", state: "Andhra Pradesh", multiplier: 1.04, arrival: "8,100 Quintals", trend: "+1.9%", trendColor: "var(--primary-700)" }
  ];

  tableBody.innerHTML = mandis.map(m => {
    const rateKg = (basePrice * m.multiplier).toFixed(2);
    const rateQuintal = (basePrice * m.multiplier * 100).toLocaleString(undefined, { maximumFractionDigits: 0 });
    return `
      <tr>
        <td><strong>${m.name}</strong></td>
        <td>${m.state}</td>
        <td>₹${rateQuintal}</td>
        <td><strong>₹${rateKg}</strong></td>
        <td>${m.arrival}</td>
        <td><span style="color: ${m.trendColor}; font-weight: 700;">${m.trend.startsWith('+') ? '▲ ' : m.trend.startsWith('-') ? '▼ ' : '▬ '}${m.trend}</span></td>
      </tr>
    `;
  }).join('');
}

function renderForecastChart(chartData, cropName) {
  const ctx = document.getElementById('market-forecast-chart');
  if (!ctx || typeof Chart === 'undefined') return;

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  if (!chartData || !chartData.history || !chartData.forecast) return;

  const history = chartData.history;
  const forecast = chartData.forecast;

  const labels = [];
  const historyPrices = [];
  const forecastPrices = [];
  const upperBounds = [];
  const lowerBounds = [];

  // Populate history
  history.forEach(item => {
    labels.push(item.date);
    historyPrices.push(item.price);
    forecastPrices.push(null);
    upperBounds.push(null);
    lowerBounds.push(null);
  });

  // Connect forecast start to last history point
  const lastHistoryPoint = history[history.length - 1];
  if (lastHistoryPoint) {
    forecastPrices[forecastPrices.length - 1] = lastHistoryPoint.price;
    upperBounds[upperBounds.length - 1] = lastHistoryPoint.price;
    lowerBounds[lowerBounds.length - 1] = lastHistoryPoint.price;
  }

  // Populate forward projections
  forecast.forEach(item => {
    labels.push(item.date);
    historyPrices.push(null);
    forecastPrices.push(item.predicted_price);
    upperBounds.push(item.upper_bound);
    lowerBounds.push(item.lower_bound);
  });

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: `${cropName} Actual Spot Price (₹/kg)`,
          data: historyPrices,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.1)',
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 2.5,
          pointHoverRadius: 5
        },
        {
          label: 'ML Projected Price (₹/kg)',
          data: forecastPrices,
          borderColor: '#16a34a',
          borderDash: [5, 5],
          backgroundColor: 'transparent',
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 3,
          pointBackgroundColor: '#16a34a'
        },
        {
          label: 'Uncertainty Upper Bound',
          data: upperBounds,
          borderColor: 'transparent',
          backgroundColor: 'rgba(34, 197, 94, 0.12)',
          fill: '+1',
          pointRadius: 0
        },
        {
          label: 'Uncertainty Lower Bound',
          data: lowerBounds,
          borderColor: 'transparent',
          backgroundColor: 'rgba(34, 197, 94, 0.12)',
          fill: false,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              if (context.raw !== null && context.raw !== undefined) {
                return `${context.dataset.label}: ₹${Number(context.raw).toFixed(2)}/kg`;
              }
              return null;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxTicksLimit: 12,
            font: { size: 11 }
          }
        },
        y: {
          grid: {
            color: '#f1f5f9'
          },
          ticks: {
            callback: function(value) {
              return '₹' + value;
            },
            font: { size: 11 }
          }
        }
      }
    }
  });
}

// Initialise event listeners on page load
document.addEventListener('DOMContentLoaded', () => {
  const runBtn = document.getElementById('btn-run-forecast');
  if (runBtn) {
    runBtn.addEventListener('click', fetchAndRenderForecast);
  }

  const cropSelect = document.getElementById('market-crop-select');
  const locSelect = document.getElementById('market-location-select');
  const horSelect = document.getElementById('market-horizon-select');

  if (cropSelect) cropSelect.addEventListener('change', fetchAndRenderForecast);
  if (locSelect) locSelect.addEventListener('change', fetchAndRenderForecast);
  if (horSelect) horSelect.addEventListener('change', fetchAndRenderForecast);

  // Initial load
  fetchAndRenderForecast();
});
