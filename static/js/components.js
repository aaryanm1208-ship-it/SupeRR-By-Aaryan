/**
 * Reusable UI Components for SupeRR Selector.
 * Renders verified statistical tables, spotlight cards, modals, and figures.
 */

const Components = {

  renderKpiCard(label, value, subtext, highlightClass = '') {
    return `
      <div class="kpi-card">
        <div>
          <div class="kpi-label">${label}</div>
          <div class="kpi-value">${value}</div>
        </div>
        <div class="kpi-subtext ${highlightClass}">${subtext}</div>
      </div>
    `;
  },

  renderSpotlightHero(batter, bowler) {
    return `
      <div class="hero-spotlight">
        <div class="spotlight-card batter-spotlight">
          <div class="spotlight-badge">#1 Ranked Batter Under Pressure</div>
          <div class="spotlight-name">${batter.name}</div>
          <div class="spotlight-archetype">${batter.tactical_archetype}</div>
          
          <div class="spotlight-stats-row">
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Composite Rating</span>
              <span class="spotlight-stat-val accent">${batter.rating}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Pressure SR</span>
              <span class="spotlight-stat-val">${batter.pressure_sr}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Clutch Delta</span>
              <span class="spotlight-stat-val accent">+${batter.sr_delta}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Runs/Dismissal</span>
              <span class="spotlight-stat-val">${batter.rpd}</span>
            </div>
          </div>
          
          <button class="btn btn-primary btn-sm" onclick="App.openPlayerModal('BATTER', ${batter.id})">
            Inspect Player Profile →
          </button>
        </div>

        <div class="spotlight-card bowler-spotlight">
          <div class="spotlight-badge">#1 Ranked Bowler Under Pressure</div>
          <div class="spotlight-name">${bowler.name}</div>
          <div class="spotlight-archetype">${bowler.tactical_archetype}</div>
          
          <div class="spotlight-stats-row">
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Composite Rating</span>
              <span class="spotlight-stat-val accent">${bowler.rating}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Pressure Economy</span>
              <span class="spotlight-stat-val">${bowler.pressure_econ}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Runs Saved / Over</span>
              <span class="spotlight-stat-val accent">+${bowler.runs_saved_per_over}</span>
            </div>
            <div class="spotlight-stat">
              <span class="spotlight-stat-label">Pressure Wickets</span>
              <span class="spotlight-stat-val">${bowler.pressure_wickets}</span>
            </div>
          </div>
          
          <button class="btn btn-primary btn-sm" onclick="App.openPlayerModal('BOWLER', ${bowler.id})">
            Inspect Player Profile →
          </button>
        </div>
      </div>
    `;
  },

  renderBatterTable(batters, sortCol, sortOrder) {
    if (!batters || batters.length === 0) {
      return `<div style="padding: 32px; text-align: center; color: var(--text-subtle);">No eligible batters matching criteria.</div>`;
    }

    const sortClass = col => col === sortCol ? (sortOrder === 'asc' ? 'sort-asc' : 'sort-desc') : '';

    const rows = batters.map(b => {
      const rankClass = b.rank === 1 ? 'rank-1' : b.rank === 2 ? 'rank-2' : b.rank === 3 ? 'rank-3' : 'rank-standard';
      const isTop10 = b.rank <= 10;
      const rowClass = isTop10 ? 'top-performer' : '';
      const deltaClass = b.sr_delta >= 0 ? 'delta-positive' : 'delta-negative';

      return `
        <tr class="${rowClass}" onclick="App.openPlayerModal('BATTER', ${b.player_id})" style="cursor: pointer;">
          <td style="text-align: center;"><span class="rank-badge ${rankClass}">${b.rank}</span></td>
          <td style="font-weight: 700;">
            ${b.player_name}
            <div style="font-size: 11px; font-weight: 500; color: var(--text-subtle);">${b.tactical_archetype}</div>
          </td>
          <td><span class="rating-badge">${b.composite_rating.toFixed(1)}</span></td>
          <td style="font-weight: 700;">${b.pressure_sr.toFixed(1)}</td>
          <td style="color: var(--text-subtle);">${b.pressure_sr_eb.toFixed(1)}</td>
          <td>${b.normal_sr.toFixed(1)}</td>
          <td><span class="delta-pill ${deltaClass}">${b.sr_delta >= 0 ? '+' : ''}${b.sr_delta.toFixed(1)}</span></td>
          <td>${b.pressure_rpd.toFixed(1)}</td>
          <td>${b.pressure_balls}</td>
          <td>${b.pressure_matches}</td>
          <td>${b.positive_contribution_pct.toFixed(1)}%</td>
          <td style="font-size: 11px; color: var(--text-subtle);">[${b.boot_sr_ci_lower.toFixed(1)}, ${b.boot_sr_ci_upper.toFixed(1)}]</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); App.openPlayerModal('BATTER', ${b.player_id})">
              Details
            </button>
          </td>
        </tr>
      `;
    }).join('');

    return `
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th class="sortable ${sortClass('rank')}" onclick="App.handleSort('batters', 'rank')">Rank</th>
              <th class="sortable ${sortClass('name')}" onclick="App.handleSort('batters', 'name')">Player Name</th>
              <th class="sortable ${sortClass('composite_rating')}" onclick="App.handleSort('batters', 'composite_rating')">Rating</th>
              <th class="sortable ${sortClass('pressure_sr')}" onclick="App.handleSort('batters', 'pressure_sr')">Pressure SR</th>
              <th class="sortable ${sortClass('pressure_sr_eb')}" onclick="App.handleSort('batters', 'pressure_sr_eb')">EB Shrunk SR</th>
              <th class="sortable ${sortClass('normal_sr')}" onclick="App.handleSort('batters', 'normal_sr')">Normal SR</th>
              <th class="sortable ${sortClass('sr_delta')}" onclick="App.handleSort('batters', 'sr_delta')">SR Δ</th>
              <th class="sortable ${sortClass('pressure_rpd')}" onclick="App.handleSort('batters', 'pressure_rpd')">RPD (Avg)</th>
              <th class="sortable ${sortClass('pressure_balls')}" onclick="App.handleSort('batters', 'pressure_balls')">Balls</th>
              <th class="sortable ${sortClass('pressure_matches')}" onclick="App.handleSort('batters', 'pressure_matches')">Matches</th>
              <th class="sortable ${sortClass('positive_contribution_pct')}" onclick="App.handleSort('batters', 'positive_contribution_pct')">Impact %</th>
              <th>95% Bootstrap CI</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  },

  renderBowlerTable(bowlers, sortCol, sortOrder) {
    if (!bowlers || bowlers.length === 0) {
      return `<div style="padding: 32px; text-align: center; color: var(--text-subtle);">No eligible bowlers matching criteria.</div>`;
    }

    const sortClass = col => col === sortCol ? (sortOrder === 'asc' ? 'sort-asc' : 'sort-desc') : '';

    const rows = bowlers.map(b => {
      const rankClass = b.rank === 1 ? 'rank-1' : b.rank === 2 ? 'rank-2' : b.rank === 3 ? 'rank-3' : 'rank-standard';
      const isTop10 = b.rank <= 10;
      const rowClass = isTop10 ? 'top-performer' : '';
      const rsaaClass = b.runs_saved_per_over >= 0 ? 'delta-positive' : 'delta-negative';

      return `
        <tr class="${rowClass}" onclick="App.openPlayerModal('BOWLER', ${b.player_id})" style="cursor: pointer;">
          <td style="text-align: center;"><span class="rank-badge ${rankClass}">${b.rank}</span></td>
          <td style="font-weight: 700;">
            ${b.player_name}
            <div style="font-size: 11px; font-weight: 500; color: var(--text-subtle);">${b.tactical_archetype}</div>
          </td>
          <td><span class="rating-badge">${b.composite_rating.toFixed(1)}</span></td>
          <td style="font-weight: 700;">${b.pressure_econ.toFixed(2)}</td>
          <td style="font-weight: 600; color: var(--color-primary-green);">${b.phase_adj_econ.toFixed(2)}</td>
          <td><span class="delta-pill ${rsaaClass}">${b.runs_saved_per_over >= 0 ? '+' : ''}${b.runs_saved_per_over.toFixed(2)}</span></td>
          <td style="font-weight: 700;">${b.pressure_wickets}</td>
          <td>${b.pressure_dot_pct.toFixed(1)}%</td>
          <td>${b.pressure_boundary_pct.toFixed(1)}%</td>
          <td>${b.clutch_spell_pct.toFixed(1)}%</td>
          <td>${b.pressure_legal_balls} (${b.pressure_matches}m)</td>
          <td style="font-size: 11px; color: var(--text-subtle);">[${b.boot_econ_ci_lower.toFixed(2)}, ${b.boot_econ_ci_upper.toFixed(2)}]</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); App.openPlayerModal('BOWLER', ${b.player_id})">
              Details
            </button>
          </td>
        </tr>
      `;
    }).join('');

    return `
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th class="sortable ${sortClass('rank')}" onclick="App.handleSort('bowlers', 'rank')">Rank</th>
              <th class="sortable ${sortClass('name')}" onclick="App.handleSort('bowlers', 'name')">Bowler Name</th>
              <th class="sortable ${sortClass('composite_rating')}" onclick="App.handleSort('bowlers', 'composite_rating')">Rating</th>
              <th class="sortable ${sortClass('pressure_econ')}" onclick="App.handleSort('bowlers', 'pressure_econ')">Press Econ</th>
              <th class="sortable ${sortClass('phase_adj_econ')}" onclick="App.handleSort('bowlers', 'phase_adj_econ')">Phase-Adj Econ</th>
              <th class="sortable ${sortClass('runs_saved_per_over')}" onclick="App.handleSort('bowlers', 'runs_saved_per_over')">Runs Saved/Ov</th>
              <th class="sortable ${sortClass('pressure_wickets')}" onclick="App.handleSort('bowlers', 'pressure_wickets')">Wkts</th>
              <th class="sortable ${sortClass('pressure_dot_pct')}" onclick="App.handleSort('bowlers', 'pressure_dot_pct')">Dot %</th>
              <th>Boundary %</th>
              <th class="sortable ${sortClass('clutch_spell_pct')}" onclick="App.handleSort('bowlers', 'clutch_spell_pct')">Clutch %</th>
              <th class="sortable ${sortClass('pressure_legal_balls')}" onclick="App.handleSort('bowlers', 'pressure_legal_balls')">Balls (M)</th>
              <th>95% Bootstrap CI</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  },

  renderResearchGallery(figures) {
    if (!figures || figures.length === 0) {
      return `<div>No figures found.</div>`;
    }

    const cards = figures.map(fig => `
      <div class="figure-card">
        <div class="figure-img-wrap" onclick="App.openLightboxModal('${fig.filename}', '${fig.title}', '${fig.description.replace(/'/g, "\\'")}', '${fig.takeaway.replace(/'/g, "\\'")}')">
          <img src="/figures/${fig.filename}" alt="${fig.title}" loading="lazy">
        </div>
        <div class="figure-info">
          <div>
            <div class="figure-title">${fig.title}</div>
            <div class="figure-desc">${fig.description}</div>
          </div>
          <div class="figure-takeaway">
            <strong>Key Insight:</strong> ${fig.takeaway}
          </div>
        </div>
      </div>
    `).join('');

    return `<div class="figures-grid">${cards}</div>`;
  }
};

window.Components = Components;

