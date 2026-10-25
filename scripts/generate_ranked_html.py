import json, html

with open("/tmp/ranked_entries_full.json") as f:
    entries = json.load(f)

# Count tiers
tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for e in entries:
    tier_counts[e["tier"]] = tier_counts.get(e["tier"], 0) + 1

tier_names = {
    1: "Tier 1: Direct Peer Replacement & Self-Recognition",
    2: "Tier 2: Undercover Probes, Stings & Say-vs-Do",
    3: "Tier 3: Statistical Monitors, Net Influence & CMI",
    4: "Tier 4: Steganography, Latent Channels & Dolos-1.5B",
    5: "Tier 5: Pricing Duopolies & Market Collusion (Gagana)"
}

tier_colors = {
    1: {"bg": "#ecfdf5", "border": "#10b981", "badge": "#059669", "text": "#065f46"},
    2: {"bg": "#eff6ff", "border": "#3b82f6", "badge": "#2563eb", "text": "#1e40af"},
    3: {"bg": "#fefce8", "border": "#eab308", "badge": "#ca8a04", "text": "#854d0e"},
    4: {"bg": "#faf5ff", "border": "#a855f7", "badge": "#9333ea", "text": "#6b21a8"},
    5: {"bg": "#f8fafc", "border": "#94a3b8", "badge": "#64748b", "text": "#334155"}
}

cards_html = []
for e in entries:
    t = e["tier"]
    tc = tier_colors[t]
    
    # Escape fields
    title_esc = html.escape(e["title"])
    author_esc = html.escape(e["author"])
    track_esc = html.escape(e["track"])
    summary_esc = html.escape(e["summary"])
    relevance_esc = html.escape(e["relevance_desc"])
    takeaway_esc = html.escape(e["takeaway"])
    url_esc = html.escape(e["url"])
    
    card = f"""
    <div class="project-card" data-tier="{t}" data-score="{e['score']}" data-rank="{e['rank']}" style="border-left: 5px solid {tc['border']};">
      <div class="card-header">
        <div class="rank-score-group">
          <span class="rank-badge" style="background-color: {tc['badge']};">#{e['rank']}</span>
          <span class="score-pill" style="background-color: {tc['bg']}; color: {tc['text']}; border: 1px solid {tc['border']};">Relevance: {e['score']}%</span>
          <span class="tier-tag" style="color: {tc['text']}; font-weight: 600;">{tier_names[t].split(':')[0]}</span>
        </div>
        <div class="track-badge">{track_esc}</div>
      </div>
      
      <h3 class="project-title">
        <a href="{url_esc}" target="_blank" rel="noopener noreferrer">{title_esc}</a>
      </h3>
      
      <div class="project-author">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        <span>{author_esc}</span>
      </div>
      
      <div class="project-abstract">
        <strong>Summary:</strong> {summary_esc}
      </div>
      
      <div class="relevance-box" style="background-color: {tc['bg']}; border-left: 3px solid {tc['border']};">
        <div class="relevance-title" style="color: {tc['text']};">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          Relevance to Our PGG Peer Detection Work
        </div>
        <p class="relevance-text">{relevance_esc}</p>
        <div class="takeaway-text"><strong>Key Actionable Takeaway:</strong> {takeaway_esc}</div>
      </div>
      
      <div class="card-footer">
        <a href="{url_esc}" target="_blank" rel="noopener noreferrer" class="link-btn">
          View on Apart Research
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        </a>
        <span class="project-id-text">ID: {e['id']}</span>
      </div>
    </div>
    """
    cards_html.append(card)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Apart Research AI Collusion Sprint — All 74 Submissions Ranked by Relevance</title>
  <style>
    :root {{
      --primary: #0f172a;
      --secondary: #334155;
      --accent: #2563eb;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
      --radius: 10px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.55;
      padding: 30px 20px 80px;
    }}
    .container {{
      max-width: 1240px;
      margin: 0 auto;
    }}
    header {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 32px 36px;
      margin-bottom: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .badge-top {{
      display: inline-block;
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 999px;
      margin-bottom: 12px;
      border: 1px solid #bfdbfe;
    }}
    h1 {{
      font-size: 28px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }}
    .subtitle {{
      font-size: 15px;
      color: var(--secondary);
      max-width: 980px;
      margin-bottom: 20px;
    }}
    .our-setup-box {{
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 18px 22px;
      font-size: 13.5px;
      color: #334155;
      margin-top: 15px;
    }}
    .our-setup-title {{
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .arms-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      margin-top: 10px;
    }}
    .arm-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 12.5px;
    }}
    .arm-card strong {{ color: #0f172a; }}
    
    .stats-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}
    .stat-box {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .stat-number {{
      font-size: 26px;
      font-weight: 800;
      color: var(--primary);
    }}
    .stat-label {{
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 500;
      margin-top: 2px;
    }}
    
    .controls-panel {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 24px;
      margin-bottom: 24px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }}
    .search-sort-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-bottom: 16px;
    }}
    .search-input-wrap {{
      flex: 1;
      min-width: 280px;
      position: relative;
    }}
    .search-input {{
      width: 100%;
      padding: 10px 14px 10px 38px;
      font-size: 14px;
      border: 1px solid var(--border);
      border-radius: 6px;
      outline: none;
      transition: all 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
    }}
    .search-icon {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
    }}
    .sort-select {{
      padding: 10px 14px;
      font-size: 14px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #ffffff;
      color: var(--text);
      cursor: pointer;
    }}
    
    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .pill-btn {{
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid var(--border);
      background: #f8fafc;
      color: var(--secondary);
      cursor: pointer;
      transition: all 0.15s;
    }}
    .pill-btn:hover {{
      background: #e2e8f0;
    }}
    .pill-btn.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}
    
    .results-count {{
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 16px;
      font-weight: 500;
    }}
    
    .projects-grid {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .project-card {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px 26px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .project-card:hover {{
      box-shadow: 0 6px 16px -2px rgba(0,0,0,0.06);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .rank-score-group {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .rank-badge {{
      color: #ffffff;
      font-size: 12px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 0.02em;
    }}
    .score-pill {{
      font-size: 12px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 999px;
    }}
    .tier-tag {{
      font-size: 12px;
    }}
    .track-badge {{
      background: #f1f5f9;
      color: #475569;
      font-size: 12px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }}
    .project-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 6px;
      line-height: 1.35;
    }}
    .project-title a {{
      color: inherit;
      text-decoration: none;
    }}
    .project-title a:hover {{
      color: var(--accent);
      text-decoration: underline;
    }}
    .project-author {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}
    .project-abstract {{
      font-size: 13.5px;
      color: #334155;
      margin-bottom: 14px;
      line-height: 1.5;
    }}
    .relevance-box {{
      border-radius: 6px;
      padding: 12px 16px;
      font-size: 13px;
      margin-bottom: 14px;
    }}
    .relevance-title {{
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
    }}
    .relevance-text {{
      color: #1e293b;
      margin-bottom: 6px;
      line-height: 1.45;
    }}
    .takeaway-text {{
      color: #0f172a;
      line-height: 1.45;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid #f1f5f9;
      padding-top: 12px;
      font-size: 12px;
    }}
    .link-btn {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
    }}
    .link-btn:hover {{
      text-decoration: underline;
    }}
    .project-id-text {{
      color: var(--text-muted);
      font-family: monospace;
      font-size: 11px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="badge-top">Apart Research Sprint Analysis</div>
      <h1>AI Collusion Research Sprint (Oct 23–25, 2026)</h1>
      <p class="subtitle">
        Comprehensive audit and relevance ranking of all <strong>74 submitted projects</strong> benchmarked directly against our research on 
        <strong>Track 3 Q3.3: Peer Detection & Model Replacement in Multi-Agent LLMs</strong> (Public Goods Game setup).
      </p>
      
      <div class="our-setup-box">
        <div class="our-setup-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          Anchor: What We've Been Cooking in Google Doc <code>1fFitfTlRKLAbkt8UfIYEGZqNCAMQUXakEfL84pRN1rA</code>
        </div>
        <div class="arms-grid">
          <div class="arm-card">
            <strong>Arm A: Statistical Monitor</strong><br>
            Non-prompting cross-perplexity, N-gram log-odds & BOCPD changepoint detection. <strong>AUC = 1.000</strong> (cross-provider), <strong>0.944</strong> (scale).
          </div>
          <div class="arm-card">
            <strong>Arm B: Dose-Response Curve</strong><br>
            8 conditions across 1,496 probes. Monotonic P3 sensitivity (0.955 free-rider &rarr; 0.493 clean rename null). Proved -1.4 trust drop was a prompt leak artifact.
          </div>
          <div class="arm-card">
            <strong>Arm C: Reasoning Double Dissociation</strong><br>
            DeepSeek-R1 test-time thinking pilot (240 probes). R1 detects defection behaviorally (AUC ~0.66) but assigns chance null (AUC = 0.500) to silent identity swaps.
          </div>
          <div class="arm-card">
            <strong>Gagana's Market Explorations</strong><br>
            Repeated Bertrand duopolies and double auctions; why LLM agents fail to sustain tacit collusion without explicit coordination scaffolds.
          </div>
        </div>
      </div>
    </header>

    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-number">{len(entries)}</div>
        <div class="stat-label">Total Sprint Submissions</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" style="color: #059669;">{tier_counts[1]}</div>
        <div class="stat-label">Tier 1: Direct Sister Projects</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" style="color: #2563eb;">{tier_counts[2]}</div>
        <div class="stat-label">Tier 2: Undercover Probes & Stings</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" style="color: #ca8a04;">{tier_counts[3]}</div>
        <div class="stat-label">Tier 3: Statistical Monitors & Net Infl.</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" style="color: #64748b;">{tier_counts[5]}</div>
        <div class="stat-label">Tier 5: Pricing Duopoly / Markets</div>
      </div>
    </div>

    <div class="controls-panel">
      <div class="search-sort-row">
        <div class="search-input-wrap">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by title, author, keyword, or takeaway...">
        </div>
        <select id="sortSelect" class="sort-select">
          <option value="rank">Sort by: Relevance Rank (#1 &rarr; #74)</option>
          <option value="score">Sort by: Relevance Score (High &rarr; Low)</option>
          <option value="title">Sort by: Project Title (A &rarr; Z)</option>
        </select>
      </div>

      <div class="filter-pills">
        <button class="pill-btn active" data-filter="all">All Projects ({len(entries)})</button>
        <button class="pill-btn" data-filter="1">Tier 1: Direct Peer Replacement ({tier_counts[1]})</button>
        <button class="pill-btn" data-filter="2">Tier 2: Stings & Say-vs-Do ({tier_counts[2]})</button>
        <button class="pill-btn" data-filter="3">Tier 3: Statistical Monitors ({tier_counts[3]})</button>
        <button class="pill-btn" data-filter="4">Tier 4: Steganography & Dolos ({tier_counts[4]})</button>
        <button class="pill-btn" data-filter="5">Tier 5: Pricing Duopolies ({tier_counts[5]})</button>
      </div>
    </div>

    <div class="results-count" id="resultsCount">Showing 74 of 74 projects</div>

    <div class="projects-grid" id="projectsGrid">
      {"".join(cards_html)}
    </div>
  </div>

  <script>
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const filterBtns = document.querySelectorAll('.pill-btn');
    const grid = document.getElementById('projectsGrid');
    const cards = Array.from(grid.querySelectorAll('.project-card'));
    const resultsCount = document.getElementById('resultsCount');

    let currentFilter = 'all';
    let currentSearch = '';
    let currentSort = 'rank';

    function update() {{
      let visible = 0;
      cards.forEach(card => {{
        const tier = card.dataset.tier;
        const text = card.textContent.toLowerCase();
        
        const matchesFilter = (currentFilter === 'all' || tier === currentFilter);
        const matchesSearch = (!currentSearch || text.includes(currentSearch));

        if (matchesFilter && matchesSearch) {{
          card.style.display = 'block';
          visible++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      resultsCount.textContent = `Showing ${{visible}} of ${{cards.length}} projects`;

      // Sorting
      const sorted = [...cards].sort((a, b) => {{
        if (currentSort === 'rank') {{
          return parseInt(a.dataset.rank) - parseInt(b.dataset.rank);
        }} else if (currentSort === 'score') {{
          return parseInt(b.dataset.score) - parseInt(a.dataset.score);
        }} else if (currentSort === 'title') {{
          const tA = a.querySelector('.project-title').textContent.trim();
          const tB = b.querySelector('.project-title').textContent.trim();
          return tA.localeCompare(tB);
        }}
        return 0;
      }});

      sorted.forEach(card => grid.appendChild(card));
    }}

    searchInput.addEventListener('input', e => {{
      currentSearch = e.target.value.toLowerCase().trim();
      update();
    }});

    sortSelect.addEventListener('change', e => {{
      currentSort = e.target.value;
      update();
    }});

    filterBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        update();
      }});
    }});
  </script>
</body>
</html>
"""

output_path = "/Users/kaustgup/Desktop/Speshal/projects/ai-collusion-research-sprint/sprint_projects_ranked.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully wrote {output_path} ({len(html_content)} bytes).")
