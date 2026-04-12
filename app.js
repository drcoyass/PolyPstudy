document.addEventListener('DOMContentLoaded', function() {
    console.log("PolyP Intelligence Portal Core Loaded.");

    const paperIndexList = document.getElementById('paperIndexList');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const lastSyncDate = document.getElementById('lastSyncDate');
    const langToggle = document.getElementById('langToggle');

    let papersData = [];
    let filteredData = [];
    let currentLang = 'ja';
    let activeCategory = 'all';
    let activeSource = 'all';
    let displayedCount = 50;

    // Load Data
    fetch('data/latest_papers.json?t=' + Date.now())
        .then(res => res.json())
        .then(data => {
            papersData = data.papers || [];
            if (lastSyncDate) lastSyncDate.innerText = "Last Synced: " + (data.generated_at || "2026.04.12");
            
            // Sync dashboard counters
            const statPapersCount = document.getElementById('statPapersCount');
            if (statPapersCount) animateValue(statPapersCount, 0, data.total_pubmed_count || 19778, 2000);
            
            const eliteCount = document.getElementById('eliteCount');
            if (eliteCount) animateValue(eliteCount, 0, papersData.length, 2000);

            // Dashboard Charts
            renderTrendsChart(data.official_stats);
            renderTopicCloud(papersData);

            performSearch();
        })
        .catch(err => console.error("Data Load Error:", err));

    function performSearch() {
        const query = (searchInput ? searchInput.value.toLowerCase().trim() : "");
        
        filteredData = papersData.filter(p => {
            const searchable = [
                p.title, p.jp_title, p.authors, p.jp_authors, p.abstract, p.summary_html,
                ...(p.tags || []), ...(p.hashtags || [])
            ].filter(Boolean).join(' ').toLowerCase();
            
            const matchesQuery = !query || searchable.includes(query);
            
            // Topic filter
            let matchesCategory = activeCategory === 'all';
            if (activeCategory === 'TOP100') matchesCategory = p.is_top_100 === true;
            else if (activeCategory === 'DENTAL100') matchesCategory = p.is_dental_top_100 === true;
            else if (activeCategory === '歯科') matchesCategory = (p.tags && p.tags.includes('歯科'));
            else if (activeCategory === '医科') matchesCategory = (p.tags && p.tags.includes('医科'));

            // Source filter
            let matchesSource = activeSource === 'all' || (p.source && p.source.toLowerCase() === activeSource.toLowerCase());
            
            return matchesQuery && matchesCategory && matchesSource;
        });

        // Smart Sort: Elite items or Newest (if no query)
        filteredData.sort((a, b) => {
            if (query) {
                // If searching, relevance logic
                return getRelevanceScore(b, query) - getRelevanceScore(a, query);
            }
            // Default: Elite first, then date
            if (a.is_top_100 && !b.is_top_100) return -1;
            if (!a.is_top_100 && b.is_top_100) return 1;
            return (b.date || "").localeCompare(a.date || "");
        });

        displayedCount = 50;
        renderLibrary();
    }

    function renderLibrary() {
        if (!paperIndexList) return;
        paperIndexList.innerHTML = '';
        
        const chunk = filteredData.slice(0, displayedCount);
        chunk.forEach(p => {
            const li = document.createElement('div');
            li.className = 'knowledge-card';
            li.onclick = () => openPaperModal(p);

            const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
            const displayAuthors = (currentLang === 'ja' && p.jp_authors) ? p.jp_authors : p.authors;
            const sourceClass = `source-${p.source ? p.source.toLowerCase() : 'pubmed'}`;
            
            li.innerHTML = `
                <div class="card-side-info">
                    <div class="card-year">${p.date ? p.date.substring(0,4) : '---'}</div>
                    <div class="card-tags-v">
                        ${(p.tags || []).slice(0,2).map(t => `<span class="tag-chip">${t}</span>`).join('')}
                    </div>
                </div>
                <div class="card-main-content">
                    <div class="card-header-row">
                        <span class="source-badge ${sourceClass}">${p.source || 'PubMed'}</span>
                    </div>
                    <div class="card-title">${displayTitle}</div>
                    <div class="card-authors">${displayAuthors}</div>
                    <div class="card-abstract-preview">${p.summary_html ? stripHtml(p.summary_html).substring(0, 150) + '...' : (p.abstract || "").substring(0, 150) + '...'}</div>
                </div>
                <div class="card-actions">
                    <button class="expand-toggle-btn">DETAILS</button>
                </div>
            `;
            paperIndexList.appendChild(li);
        });

        // Load More Button state
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = (displayedCount < filteredData.length) ? 'block' : 'none';
        }
    }

    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.onclick = () => {
            displayedCount += 100;
            renderLibrary();
        };
    }

    window.filterByCategory = function(category) {
        activeCategory = category;
        document.querySelectorAll('#categoryFilters .filter-btn').forEach(btn => {
            const label = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
            btn.classList.toggle('active', label === category);
        });
        performSearch();
    };

    window.filterBySource = function(source) {
        activeSource = source;
        document.querySelectorAll('#sourceFilters .filter-btn').forEach(btn => {
            const label = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
            btn.classList.toggle('active', label === source);
        });
        performSearch();
    };

    // Modal Control
    const modal = document.getElementById('paperModal');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = document.getElementById('closeModal');
    if (closeBtn) closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };

    function openPaperModal(p) {
        const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
        const displayAuthors = (currentLang === 'ja' && p.jp_authors) ? p.jp_authors : p.authors;
        const bodyText = p.summary_html || `<p>${p.abstract}</p>`;
        
        modalBody.innerHTML = `
            <div style="margin-bottom: 2rem;">
                ${(p.tags || []).map(t => `<span class="tag-chip">${t}</span>`).join(' ')}
            </div>
            <h2 style="font-size: 2.2rem; margin-bottom: 1rem;">${displayTitle}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">📝 ${displayAuthors} | 📅 ${p.date} | ${p.id}</p>
            <div class="glass-card" style="padding: 2rem; margin-bottom: 2rem;">
                ${bodyText}
            </div>
            <div>
                <button class="primary-btn" onclick="window.open('${p.url}', '_blank')">View Source ↗</button>
            </div>
        `;
        modal.style.display = "block";
    }

    // Helpers
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    function renderTrendsChart(stats) {
        const trendChart = document.getElementById('trendChart');
        if (!trendChart || !stats) return;
        trendChart.innerHTML = '';
        const years = Object.keys(stats).sort();
        const max = Math.max(...Object.values(stats));
        years.forEach(y => {
            const val = stats[y];
            const height = (val / max) * 100;
            const bar = document.createElement('div');
            bar.className = 'trend-bar';
            bar.style.height = height + '%';
            bar.innerHTML = `<span class="trend-bar-value">${val}</span><span class="trend-bar-inner">${y}</span>`;
            trendChart.appendChild(bar);
        });
    }

    function renderTopicCloud(data) {
        const topicCloud = document.getElementById('topicCloud');
        if (!topicCloud) return;
        const counts = {};
        data.forEach(p => { (p.tags || []).forEach(t => counts[t] = (counts[t] || 0) + 1); });
        const sorted = Object.keys(counts).sort((a,b) => counts[b] - counts[a]).slice(0, 15);
        topicCloud.innerHTML = sorted.map(t => `<div class="topic-item"># ${t} <span>${counts[t]}</span></div>`).join('');
    }

    function getRelevanceScore(p, q) {
        let s = 0; q = q.toLowerCase();
        if (p.title.toLowerCase().includes(q)) s += 10;
        if (p.jp_title && p.jp_title.toLowerCase().includes(q)) s += 10;
        if ((p.tags || []).some(t => t.toLowerCase().includes(q))) s += 5;
        return s;
    }

    function stripHtml(html) {
        const tmp = document.createElement("DIV");
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || "";
    }

    if (searchBtn) searchBtn.onclick = performSearch;
    if (searchInput) searchInput.oninput = performSearch;
});
