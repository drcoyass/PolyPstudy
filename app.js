document.addEventListener('DOMContentLoaded', function() {
    console.log("PolyP Intelligence Portal Core: World-Class Performance Optimized.");

    const paperIndexList = document.getElementById('paperIndexList');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const lastSyncDate = document.getElementById('lastSyncDate');
    const initialLoader = document.getElementById('initial-loader');
    const loadingProgress = document.getElementById('loading-progress');
    const langToggle = document.getElementById('langToggle');

    let papersData = [];
    let filteredData = [];
    let currentLang = 'ja';
    let activeCategory = 'all';
    let activeSource = 'all';
    let displayedCount = 50;
    
    const translations = {
        ja: {
            loadingText: "19,000件の論文データを同期中...",
            navResearch: "論文検索",
            navNetwork: "ネットワーク",
            navStory: "歴史",
            heroTitle: "ポリリン酸の起源を解き明かす<br><span class=\"highlight\">Poly-P</span>",
            searchPlaceholder: "論文タイトル、著者、または分子キーワードで検索...",
            btnSearch: "検索",
            btnLoadMore: "さらに読み込む ▽"
        },
        en: {
            loadingText: "Syncing 19,000 research records...",
            navResearch: "Research",
            navNetwork: "Network",
            navStory: "Story",
            heroTitle: "Unlocking the Origins of <br><span class=\"highlight\">Poly-P</span>",
            searchPlaceholder: "Search by paper title, authors, or molecular keywords...",
            btnSearch: "SEARCH",
            btnLoadMore: "LOAD MORE ▽"
        }
    };

    function updateLanguage() {
        // Simple placeholder for i18n
        if (langToggle) langToggle.textContent = currentLang === 'ja' ? 'EN' : '日本語';
        const t = translations[currentLang];
        if (searchInput) searchInput.placeholder = t.searchPlaceholder;
        if (searchBtn) searchBtn.textContent = t.btnSearch;
        renderLibrary();
    }

    if (langToggle) {
        langToggle.addEventListener('click', () => {
            currentLang = currentLang === 'ja' ? 'en' : 'ja';
            updateLanguage();
        });
    }

    // --- High-End Loading Sequence ---
    const loadingInterval = setInterval(() => {
        let progress = parseInt(loadingProgress.style.width || 0);
        if (progress < 90) loadingProgress.style.width = (progress + 5) + '%';
    }, 100);

    const finishLoading = () => {
        clearInterval(loadingInterval);
        if (loadingProgress) loadingProgress.style.width = '100%';
        setTimeout(() => {
            if (initialLoader) {
                initialLoader.classList.add('fade-out');
                setTimeout(() => initialLoader.style.display = 'none', 800);
            }
        }, 500);
    };

    // --- 究極の2段階ロード・エンジン ---
    // 1. summary.json (2KB) を最優先で読み込み、一瞬でダッシュボードを表示
    fetch('data/summary.json?t=' + Date.now())
        .then(res => res.json())
        .then(summary => {
            if (lastSyncDate) lastSyncDate.innerText = "最終同期日: " + (summary.generated_at || "2026.04.14");
            const statPapersCount = document.getElementById('statPapersCount');
            if (statPapersCount) animateValue(statPapersCount, 0, summary.total_pubmed_count || 19778, 1000);
            const eliteCount = document.getElementById('eliteCount');
            if (eliteCount) animateValue(eliteCount, 0, summary.elite_count || 4204, 1000);

            renderTrendsChart(summary.official_stats || summary.global_historical_stats);
            renderTopicCloudFromSummary(summary.global_topic_stats);

            // 2. 表示完了後に背後で 22MB の巨大データをロード
            return fetch('data/latest_papers.json?t=' + Date.now());
        })
        .then(res => res.json())
        .then(data => {
            papersData = data.papers || [];
            filteredData = [...papersData];
            finishLoading();
            performSearch();
        })
        .catch(err => {
            console.error("Load Error:", err);
            finishLoading();
        });

    function animateValue(obj, start, end, duration) {
        if (!obj) return;
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
        
        // 画面幅に応じて棒の太さを動的に調整（デスクトップでの突き抜けを防止）
        const isMobile = window.innerWidth < 768;
        
        years.forEach(y => {
            const bar = document.createElement('div');
            bar.className = 'trend-bar';
            bar.style.flex = "1";
            bar.style.height = (stats[y] / max * 100) + '%';
            // モバイルなら指で触りやすい太さを維持、デスクトップなら枠に収める
            bar.style.minWidth = isMobile ? "25px" : "1px"; 
            bar.style.cursor = 'pointer';
            bar.onclick = () => {
                if (searchInput) {
                    searchInput.value = y;
                    performSearch();
                    document.getElementById('papers').scrollIntoView({ behavior: 'smooth' });
                }
            };
            bar.innerHTML = `
                <span class="trend-bar-value">${stats[y]}</span>
                <span class="trend-bar-inner">${y}</span>
            `;
            trendChart.appendChild(bar);
        });

        // Use more robust scrolling logic for mobile
        requestAnimationFrame(() => {
            setTimeout(() => {
                const chartArea = document.querySelector('.dashboard-chart-area');
                if (chartArea) {
                    chartArea.scrollTo({
                        left: chartArea.scrollWidth,
                        behavior: 'smooth'
                    });
                }
            }, 800);
        });
    }

    function renderTopicCloudFromSummary(counts) {
        const topicCloud = document.getElementById('topicCloud');
        if (!topicCloud || !counts) return;
        const sorted = Object.keys(counts).sort((a,b) => counts[b] - counts[a]).slice(0, 15);
        topicCloud.innerHTML = sorted.map(t => `
            <div class="topic-item" onclick="window.filterByTag('${t}')">
                <span class="topic-name">${t}</span>
                <span class="topic-count">${counts[t].toLocaleString()}</span>
            </div>
        `).join('');
    }

    window.filterByTag = function(tag) {
        if (!searchInput) return;
        searchInput.value = tag;
        performSearch();
        document.getElementById('papers').scrollIntoView({ behavior: 'smooth' });
    };

    function performSearch() {
        if (!searchInput) return;
        let query = searchInput.value.toLowerCase().trim();
        displayedCount = 50;

        if (!query) {
            filteredData = [...papersData];
        } else {
            filteredData = papersData.filter(p => {
                const text = (p.title + (p.jp_title || "") + p.authors + (p.tags || []).join(" ")).toLowerCase();
                return text.includes(query);
            });
        }
        renderLibrary();
    }

    function renderLibrary() {
        if (!paperIndexList) return;
        paperIndexList.innerHTML = '';
        const items = filteredData.slice(0, displayedCount);
        
        if (items.length === 0) {
            paperIndexList.innerHTML = '<div class="empty-state">No matching research found.</div>';
            return;
        }

        items.forEach((p, i) => {
            const card = document.createElement('div');
            card.className = 'knowledge-card';
            
            const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
            const displayAuthors = (p.authors || "Academic Record");
            const btnLabel = currentLang === 'ja' ? '詳細解析' : 'DETAIL';
            
            // 論文の権威性を示すバッジ類
            card.innerHTML = `
                <div class="card-side-info">
                    <div class="year-badge">${p.year || '---'}</div>
                    <div class="source-badge">PUBMED</div>
                </div>
                <div class="card-main-content">
                    <div class="card-header-row" style="margin-bottom: 0.5rem; opacity: 0.6; font-size: 0.75rem;">
                        <span>PMID: ${p.id}</span>
                    </div>
                    <div class="card-title">${displayTitle}</div>
                    <div class="card-authors-row" style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent-primary); opacity: 0.8;">${displayAuthors}</div>
                </div>
                <div class="card-actions-v">
                    <button class="primary-btn" onclick="window.openPaperModal(${i})" style="width: 100%; border-radius: 8px; padding: 0.8rem;">
                        ${btnLabel}
                    </button>
                </div>
            `;
            paperIndexList.appendChild(card);
        });
        
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) loadMoreBtn.style.display = (displayedCount < filteredData.length) ? 'block' : 'none';
    }

    window.openPaperModal = function(index) {
        const p = filteredData[index];
        if (!p) return;
        const modal = document.getElementById('paperModal');
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <h2>${(currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title}</h2>
            <p style="margin-top:2rem; line-height:1.8;">${p.summary_jp || p.abstract || "No abstract available."}</p>
            <div style="margin-top:2rem;">
                <a href=\"https://pubmed.ncbi.nlm.nih.gov/${p.id}/\" target=\"_blank\" class=\"primary-btn\">VIEW SOURCE ↗</a>
            </div>
        `;
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    };

    window.openPosterModal = function() {
        const modal = document.getElementById('posterModal');
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    };

    const closeModal = () => {
        document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
        document.body.style.overflow = 'auto';
    };
    
    document.querySelectorAll('.close-modal').forEach(btn => btn.onclick = closeModal);
    window.onclick = (e) => { if (e.target.classList.contains('modal')) closeModal(); };

    if (searchBtn) searchBtn.onclick = performSearch;
    if (searchInput) searchInput.oninput = performSearch;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) loadMoreBtn.onclick = () => { displayedCount += 50; renderLibrary(); };
});
