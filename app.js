document.addEventListener('DOMContentLoaded', function() {
    console.log("PolyP Intelligence Portal Core: Performance Optimized.");

    const paperIndexList = document.getElementById('paperIndexList');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const lastSyncDate = document.getElementById('lastSyncDate');
    const initialLoader = document.getElementById('initial-loader');
    const loadingProgress = document.getElementById('loading-progress');

    let papersData = [];
    let filteredData = [];
    let currentLang = 'ja';
    let activeCategory = 'all';
    let activeSource = 'all';
    let displayedCount = 50;

    // --- High-End Loading Sequence ---
    const startLoadingAnimation = () => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 8;
            if (progress > 95) {
                progress = 95;
                clearInterval(interval);
            }
            if (loadingProgress) loadingProgress.style.width = `${progress}%`;
        }, 80);
        return interval;
    };

    const finishLoading = (interval) => {
        clearInterval(interval);
        if (loadingProgress) loadingProgress.style.width = '100%';
        setTimeout(() => {
            if (initialLoader) initialLoader.classList.add('fade-out');
            setTimeout(() => {
                if (initialLoader) initialLoader.style.display = 'none';
            }, 800);
        }, 500);
    };

    const loadingInterval = startLoadingAnimation();

    // --- Global Function Assignments ---
    window.openPaperSource = function(url, event) {
        if (event && event.stopPropagation) event.stopPropagation();
        if (!url || url === 'undefined') return;
        window.open(url, '_blank');
    };

    window.openPaperModalFromIndex = function(index, event) {
        if (event && event.stopPropagation) event.stopPropagation();
        
        const p = filteredData[index];
        if (!p) return;
        
        const modal = document.getElementById('paperModal');
        const modalBody = document.getElementById('modalBody');
        if (!modal || !modalBody) return;

        // 医学的・科学的に正しい日本語があれば優先
        const displayTitle = (p.jp_title || p.title);
        const displayAuthors = (p.jp_authors || p.authors);
        
        // 日本語抄録（jp_abstract or summary_jp）を最優先。なければ summary_html か abstract
        let bodyText = "";
        if (p.summary_jp && p.summary_jp.length > 10) {
            bodyText = `<div class="jp-abstract">${p.summary_jp}</div>`;
        } else if (p.jp_abstract && p.jp_abstract.length > 10) {
            bodyText = `<div class="jp-abstract">${p.jp_abstract}</div>`;
        } else if (p.summary_html && p.summary_html.length > 50) {
            bodyText = p.summary_html;
        } else {
            bodyText = `<p style="padding:1.5rem; line-height:1.8; color: #cbd5e1;">${p.abstract || '抄録データが現在登録されていません。'}</p>`;
        }

        const sourceUrl = getPaperSourceUrl(p).replace(/'/g, "\\'");
        const pdfSearchUrl = `https://scholar.google.com/scholar?q=${encodeURIComponent(p.title)}+filetype:pdf`;

        modalBody.innerHTML = `
            <div style="margin-bottom: 2rem; display: flex; gap: 0.8rem; flex-wrap: wrap;">
                ${(p.tags || []).map(t => `<span class="tag-chip" style="background: rgba(34, 211, 238, 0.2); color: var(--accent-cyan); padding: 0.4rem 1rem; border-radius: 50px; font-size: 0.8rem; border: 1px solid var(--accent-cyan);">${t}</span>`).join('')}
            </div>
            
            <h2 style="font-size: 2rem; line-height: 1.4; margin-bottom: 1.5rem; color: #fff; font-family: 'Noto Sans JP', sans-serif; font-weight: 700;">${displayTitle}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1.5rem;">📝 ${displayAuthors} | 📅 ${p.date} | ID: ${p.id}</p>
            
            <div class="glass-card" style="padding: 2.5rem; margin-bottom: 2.5rem; line-height: 1.9; font-size: 1.1rem; border-left: 6px solid var(--accent-gold); background: rgba(15, 23, 42, 0.5); border-radius: 20px;">
                <h3 style="margin-bottom: 1.5rem; color: var(--accent-gold); font-size: 0.85rem; letter-spacing: 2px; font-weight: 800; text-transform: uppercase;">Scientific Abstract / 研究概要</h3>
                <div class="abstract-content" style="color: #e2e8f0; word-break: break-word;">${bodyText}</div>
            </div>

            <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 3rem;">
                <button class="primary-btn" onclick="window.openPaperSource('${sourceUrl}')" style="min-width: 240px; padding: 1.2rem 2rem; font-size: 0.95rem; border-radius: 50px; cursor: pointer; transition: 0.3s;">SOURCE ↗ (外部サイトで全文を読む)</button>
                <button class="secondary-btn" onclick="window.open('${pdfSearchUrl}', '_blank')" style="padding: 1.2rem 2rem; font-size: 0.95rem; border-radius: 50px; cursor: pointer; border: 1px solid var(--border-glass);">SEARCH PDF (Scholar)</button>
            </div>
        `;
        
        modal.style.display = "block";
        modal.style.zIndex = "99999";
        document.body.style.overflow = "hidden";
    };

    window.filterByTag = function(tag) {
        if (!tag) return;
        if (searchInput) {
            searchInput.value = tag;
            performSearch();
            const papersSection = document.getElementById('papers');
            if (papersSection) papersSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // Load Data
    fetch('data/latest_papers.json?t=' + Date.now())
        .then(res => res.json())
        .then(data => {
            papersData = data.papers || [];
            finishLoading(loadingInterval);
            
            if (lastSyncDate) lastSyncDate.innerText = "最終同期日: " + (data.generated_at || "2026.04.12");
            
            const statPapersCount = document.getElementById('statPapersCount');
            if (statPapersCount) animateValue(statPapersCount, 0, data.total_pubmed_count || 19017, 1500);
            
            const eliteCount = document.getElementById('eliteCount');
            if (eliteCount) animateValue(eliteCount, 0, papersData.length, 1500);

            renderTrendsChart(data.official_stats);
            renderTopicCloud(papersData);
            performSearch();
        })
        .catch(err => {
            console.error("Data Load Error:", err);
            finishLoading(loadingInterval);
        });

    function performSearch() {
        const query = (searchInput ? searchInput.value.toLowerCase().trim() : "");
        
        filteredData = papersData.filter(p => {
            const searchable = [
                p.title, p.jp_title, p.authors, p.jp_authors, p.abstract, p.summary_html,
                ...(p.tags || []), ...(p.hashtags || [])
            ].filter(Boolean).join(' ').toLowerCase();
            
            const matchesQuery = !query || searchable.includes(query);
            let matchesCategory = activeCategory === 'all';
            if (activeCategory === 'TOP100') matchesCategory = p.is_top_100 === true;
            else if (activeCategory === 'DENTAL100') matchesCategory = p.is_dental_top_100 === true;
            else if (activeCategory === '歯科') matchesCategory = (p.tags && p.tags.includes('歯科'));
            else if (activeCategory === '医科') matchesCategory = (p.tags && p.tags.includes('医科'));

            let matchesSource = activeSource === 'all' || (p.source && p.source.toLowerCase() === activeSource.toLowerCase());
            return matchesQuery && matchesCategory && matchesSource;
        });

        filteredData.sort((a, b) => {
            if (query) return getRelevanceScore(b, query) - getRelevanceScore(a, query);
            if (a.is_top_100 && !b.is_top_100) return -1;
            if (!a.is_top_100 && b.is_top_100) return 1;
            return (b.date || "").localeCompare(a.date || "");
        });

        displayedCount = 50;
        renderLibrary();
    }

    function getPaperSourceUrl(p) {
        if (p.url && p.url.trim() !== "") return p.url;
        const source = (p.source || "").toLowerCase();
        const id = (p.id || "").toString();
        if (source === "pubmed" || (!source && !isNaN(id) && id !== "")) {
            return `https://pubmed.ncbi.nlm.nih.gov/${id.trim()}/`;
        } else if (source === "j-stage") {
            return `https://www.jstage.jst.go.jp/result/global/-char/ja?globalSearchKey=${encodeURIComponent(p.title)}`;
        } else if (source === "cinii") {
            return `https://ci.nii.ac.jp/search?q=${encodeURIComponent(p.title)}`;
        }
        return `https://scholar.google.com/scholar?q=${encodeURIComponent(p.title)}`;
    }

    function renderLibrary() {
        if (!paperIndexList) return;
        paperIndexList.innerHTML = '';
        
        if (filteredData.length === 0) {
            paperIndexList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>該当する知見が見つかりませんでした</h3>
                    <p>キーワードを少し変えるか、インプラント・歯科・骨再生などの主要カテゴリから探索を広げてみてください。</p>
                    <button class="secondary-btn" onclick="document.getElementById('searchInput').value=''; performSearch();">すべての論文を表示</button>
                </div>
            `;
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
            return;
        }

        const chunk = filteredData.slice(0, displayedCount);
        chunk.forEach((p, index) => {
            const li = document.createElement('div');
            li.className = 'knowledge-card';
            li.onclick = (e) => window.openPaperModalFromIndex(index, e);

            const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
            const displayAuthors = (currentLang === 'ja' && p.jp_authors) ? p.jp_authors : p.authors;
            const sourceUrl = getPaperSourceUrl(p).replace(/'/g, "\\'");
            const sourceClass = `source-${p.source ? p.source.toLowerCase().replace(/[^a-z]/g, '-') : 'pubmed'}`;
            
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
                    <div class="card-abstract-preview">
                        ${p.summary_html ? stripHtml(p.summary_html).substring(0, 180) + '...' : (p.abstract || "").substring(0, 180) + '...'}
                    </div>
                </div>
                <div class="card-actions">
                    <button class="primary-btn abstract-btn" onclick="window.openPaperModalFromIndex(${index}, event)">概要表示</button>
                    <button class="primary-btn source-jump-btn" onclick="window.openPaperSource('${sourceUrl}', event)">ソース ↗</button>
                </div>
            `;
            paperIndexList.appendChild(li);
        });

        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) loadMoreBtn.style.display = (displayedCount < filteredData.length) ? 'block' : 'none';
    }

    // Filter Listeners
    document.querySelectorAll('#categoryFilters .filter-btn').forEach(btn => {
        btn.onclick = () => {
            activeCategory = btn.getAttribute('data-category');
            document.querySelectorAll('#categoryFilters .filter-btn').forEach(b => b.classList.toggle('active', b === btn));
            performSearch();
        };
    });
    document.querySelectorAll('#sourceFilters .filter-btn').forEach(btn => {
        btn.onclick = () => {
            activeSource = btn.getAttribute('data-source');
            document.querySelectorAll('#sourceFilters .filter-btn').forEach(b => b.classList.toggle('active', b === btn));
            performSearch();
        };
    });

    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.onclick = () => {
            displayedCount += 100;
            renderLibrary();
        };
    }

    // --- Hero Section Buttons ---
    // Smooth scroll for hero buttons
    document.querySelectorAll('.hero-actions a[href^="#"]').forEach(anchor => {
        anchor.onclick = function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        };
    });

    // Special handling for PPTX download visibility and tracking
    const pptxBtn = document.getElementById('pptxDownloadBtn');
    if (pptxBtn) {
        pptxBtn.onclick = function(e) {
            console.log("Downloading Monthly Report PPTX...");
            // ブラウザのデフォルト動作（ダウンロード）を継続させるため preventDefault はしない
        };
    }

    const modal = document.getElementById('paperModal');
    const closeBtn = document.getElementById('closeModal');
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.style.display = "none";
            document.body.style.overflow = "auto";
        };
    }
    window.onclick = (e) => {
        if (e.target == modal) {
            modal.style.display = "none";
            document.body.style.overflow = "auto";
        }
    };

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
        const max = Math.max(...Object.values(stats), 1);
        years.forEach(y => {
            const bar = document.createElement('div');
            bar.className = 'trend-bar';
            bar.style.height = (stats[y] / max * 100) + '%';
            bar.innerHTML = `<span class="trend-bar-value">${stats[y]}</span><span class="trend-bar-inner">${y}</span>`;
            trendChart.appendChild(bar);
        });
    }

    function renderTopicCloud(data) {
        const topicCloud = document.getElementById('topicCloud');
        if (!topicCloud) return;
        const counts = {};
        data.forEach(p => { (p.tags || []).forEach(t => counts[t] = (counts[t] || 0) + 1); });
        const sorted = Object.keys(counts).sort((a,b) => counts[b] - counts[a]).slice(0, 15);
        topicCloud.innerHTML = sorted.map(t => `<div class="topic-item" onclick="window.filterByTag('${t}')" style="cursor: pointer;"># ${t} <span>${counts[t]}</span></div>`).join('');
    }

    function getRelevanceScore(p, q) {
        let s = 0; q = q.toLowerCase();
        if (p.title.toLowerCase().includes(q)) s += 10;
        if (p.jp_title && p.jp_title.toLowerCase().includes(q)) s += 10;
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
