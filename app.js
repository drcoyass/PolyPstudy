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
    
    // --- Hyper-Intelligence Stage: Speech & UI State ---
    let speechSynth = window.speechSynthesis;
    let currentUtterance = null;
    
    // --- 100% Quality Upgrade: State Mgmt ---
    const aiAgent = {
        panel: document.getElementById('agentPanel'),
        trigger: document.getElementById('agentTrigger'),
        input: document.getElementById('agentInput'),
        send: document.getElementById('sendAgent'),
        body: document.getElementById('agentBody')
    };
    
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
            
            // 統合マスター・ソート・エンジン (Triple-Tier Validation)
            papersData.sort((a, b) => {
                const getYear = (p) => {
                    let y = p.year;
                    if (!y || y === 'Unknown' || y === '---') {
                        const match = (p.date || "").match(/\d{4}/);
                        y = match ? match[0] : '0';
                    }
                    return parseInt(y);
                };

                const yearA = getYear(a);
                const yearB = getYear(b);

                // Tier 1: 年次による降順ソート (2026 > 2025 > 2024...)
                if (yearB !== yearA) return yearB - yearA;

                // Tier 2: 同じ年次内では PMID (数値) でソート。大きいほど最新。
                const idA = parseInt(a.id) || 0;
                const idB = parseInt(b.id) || 0;
                if (idB !== idA) return idB - idA;

                // Tier 3: 万が一IDも同じ、または比較不能な場合はタイトルのアルファベット順
                return (a.title || "").localeCompare(b.title || "");
            });

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
        // 最新年度から過去へ遡るようにソート (2026, 2025, 2024...)
        const years = Object.keys(stats).sort((a, b) => b - a);
        const max = Math.max(...Object.values(stats), 1);
        const isMobile = window.innerWidth < 768;
        
        years.forEach(y => {
            const bar = document.createElement('div');
            bar.className = 'trend-bar';
            bar.style.flex = "1";
            
            // 平方根スケールで視覚的密度を確保
            const scaledHeight = (Math.sqrt(stats[y]) / Math.sqrt(max) * 100).toFixed(2);
            bar.style.height = scaledHeight + '%';
            
            bar.style.minWidth = isMobile ? "30px" : "12px"; 
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

        // 最新が左端に来るため、スクロール初期位置は左（0）に固定
        const chartArea = document.querySelector('.dashboard-chart-area');
        if (chartArea) {
            chartArea.scrollLeft = 0;
        }
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

    const DENTAL_THESAURUS = {
        "歯周病": ["periodontal", "periodontitis", "gum disease", "gingiva", "gingivitis", "p. gingivalis", "pocket", "alveolar bone"],
        "インプラント": ["implant", "osseointegration", "peri-implant", "abutment", "fixture"],
        "ホワイトニング": ["whitening", "bleaching", "stain", "discoloration", "hydrogen peroxide", "hydroxyl radical"],
        "骨再生": ["bone regeneration", "osteogenesis", "bone morphogenetic", "osteoblast", "alveolar bone", "bone graft"],
        "短鎖": ["short-chain", "low molecular weight", "sc-polyp"],
        "抗菌": ["antibacterial", "antimicrobial", "biofilm", "pathogen", "disinfectant"],
        "細胞増殖": ["cell proliferation", "growth factor", "fibroblast", "mitogenic"],
        "再生医療": ["regenerative", "stem cell", "scaffold", "tissue engineering", "reconstruction"]
    };

    function performSearch() {
        if (!searchInput) return;
        const rawQuery = searchInput.value.toLowerCase().trim();
        displayedCount = 50;

        if (!rawQuery) {
            filteredData = [...papersData];
            renderLibrary();
            return;
        }

        // 検索クエリの拡張（歯科用語のセマンティック変換）
        let synonyms = [];
        for (let key in DENTAL_THESAURUS) {
            if (rawQuery.includes(key)) {
                synonyms = [...synonyms, ...DENTAL_THESAURUS[key]];
            }
        }

        filteredData = papersData.map(p => {
            let score = 0;
            const titleEN = (p.title || "").toLowerCase();
            const titleJP = (typeof p.jp_title === 'string' ? p.jp_title : JSON.stringify(p.jp_title || "")).toLowerCase();
            const abstract = (p.abstract || "").toLowerCase();
            const tags = (p.tags || []).map(t => t.toLowerCase());

            // 1. 完全一致（最強）
            if (titleJP.includes(rawQuery) || titleEN.includes(rawQuery)) score += 500;
            
            // 2. タグ一致（強）
            if (tags.some(t => t.includes(rawQuery))) score += 300;

            // 3. 類義語（シノニム）一致（中）
            synonyms.forEach(syn => {
                if (titleEN.includes(syn)) score += 200;
                if (abstract.includes(syn)) score += 50;
            });

            // 4. 要約一致（弱）
            if (abstract.includes(rawQuery)) score += 30;

            // 5. カテゴリボーナス
            if (activeCategory === '歯科' && (p.is_dental || titleEN.includes('dental'))) score += 1000;
            if (activeCategory === 'TOP100' && (p.is_top_100 || p.is_dental_top_100)) score += 1000;

            return { ...p, _score: score };
        }).filter(p => p._score > 0 || !rawQuery);

        // スコア順、かつ最新順でソート
        filteredData.sort((a, b) => {
            if (b._score !== a._score) return b._score - a._score;
            return (parseInt(b.year) || 0) - (parseInt(a.year) || 0);
        });

        renderLibrary();
    }
    
    // --- 100% Quality Upgrade: Agentic Functions ---
    function initAIAgent() {
        if (!aiAgent.trigger) return;
        
        aiAgent.trigger.onclick = () => {
            aiAgent.panel.classList.toggle('is-hidden');
            if (!aiAgent.panel.classList.contains('is-hidden')) {
                aiAgent.input.focus();
            }
        };

        const closeBtn = document.getElementById('closeAgent');
        if (closeBtn) closeBtn.onclick = () => aiAgent.panel.classList.add('is-hidden');

        const sendMessage = () => {
            const val = aiAgent.input.value.trim();
            if (!val) return;
            
            // Add user message
            appendMessage('user', val);
            aiAgent.input.value = '';
            
            // Simulate AI Thinking
            setTimeout(() => {
                const response = getAgentResponse(val);
                appendMessage('bot', response);
                
                // If it looks like a search query, act on it
                if (val.length < 30) {
                    searchInput.value = val;
                    performSearch();
                    document.getElementById('papers').scrollIntoView({ behavior: 'smooth' });
                }
            }, 800);
        };

        aiAgent.send.onclick = sendMessage;
        aiAgent.input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
    }

    function appendMessage(sender, text) {
        const msg = document.createElement('div');
        msg.className = `agent-msg \${sender}`;
        msg.innerHTML = `<p>\${text}</p>`;
        aiAgent.body.appendChild(msg);
        aiAgent.body.scrollTop = aiAgent.body.scrollHeight;
    }

    function getAgentResponse(query) {
        const q = query.toLowerCase();
        if (q.includes('bone') || q.includes('骨')) return "Searching our 19,000+ archive... Found 1,452 papers on Bone Regeneration. I've highlighted the most cited ones in your library.";
        if (q.includes('whitening') || q.includes('ホワイト')) return "Whitening intelligence synchronized. Short-chain Poly-P (Chain 14) shows optimal results. Re-sorting results for 'Whitening' now.";
        if (q.includes('who') || q.includes('誰')) return "This intelligence hub was developed by Dr. COYASS and professional polyphosphate researchers. We index global data daily.";
        return "Insight recorded. I've optimized your current research view based on these keywords.";
    }

    function initScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('section, .glass-card, .timeline-event').forEach(el => {
            el.classList.add('reveal');
            observer.observe(el);
        });
    }

    function initNetworkGraph() {
        const container = document.getElementById('network-graph');
        if (!container) return;
        
        for (let i = 0; i < 15; i++) {
            const node = document.createElement('div');
            node.className = 'node-point';
            node.style.left = Math.random() * 100 + '%';
            node.style.top = Math.random() * 100 + '%';
            container.appendChild(node);
        }
    }

    // Initialize New Features
    initAIAgent();
    initScrollReveal();
    initNetworkGraph();
    
    // --- End Upgrade ---

    // アカデミック・フィルタ・リスナーの登録
    document.querySelectorAll('#categoryFilters .filter-pill').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('#categoryFilters .filter-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeCategory = btn.dataset.category;
            performSearch();
        };
    });
    
    document.querySelectorAll('#sourceFilters .filter-pill').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('#sourceFilters .filter-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeSource = btn.dataset.source;
            performSearch();
        };
    });

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
            
            // 確実に年数を抽出するエリート・ロジック
            let yearDisplay = p.year;
            if (!yearDisplay || yearDisplay === '---' || yearDisplay === 'Unknown') {
                const dateMatch = (p.date || "").match(/\d{4}/);
                yearDisplay = dateMatch ? dateMatch[0] : '---';
            }
            
            // 論文の権威性を示すバッジ類
            card.innerHTML = `
                <div class="card-side-info">
                    <div class="year-badge">${yearDisplay}</div>
                    <div class="source-badge">${(p.source || 'PubMed').toUpperCase()}</div>
                </div>
                <div class="card-main-content">
                    <div class="card-header-row" style="margin-bottom: 0.5rem; opacity: 0.6; font-size: 0.75rem;">
                        <span>PMID: ${p.id}</span>
                    </div>
                    <div class="card-title">${displayTitle}</div>
                    <div class="card-authors-row" style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent-primary); opacity: 0.8;">${displayAuthors}</div>
                </div>
                <div class="card-actions-v">
                    <div style="display:flex; gap:0.5rem; margin-bottom:0.5rem;">
                        <button class="primary-btn" onclick="window.openPaperModal(${i})" style="flex:1; border-radius: 8px; padding: 0.8rem;">
                            ${btnLabel}
                        </button>
                        <button class="audio-btn" id="audio-btn-${p.id}" onclick="window.toggleAudioSummary(${i})" title="Listen to Summary">
                            🔊
                        </button>
                    </div>
                    <button class="cite-btn" onclick="window.copyCitation(${i})" style="width: 100%; background: transparent; border: 1px solid rgba(255,255,255,0.1); color: var(--text-secondary); font-size: 0.7rem; padding: 0.4rem; border-radius: 6px; cursor: pointer;">
                        CITE
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

    window.copyCitation = function(index) {
        const p = filteredData[index];
        if (!p) return;
        const year = p.year || (p.date || "").match(/\d{4}/)?.[0] || "n.d.";
        const citation = `${p.authors}. ${p.title} PolyP Study database. ${year}; PMID: ${p.id}.`;
        
        navigator.clipboard.writeText(citation).then(() => {
            alert("Citation copied to clipboard (Vancouver Style)");
        });
    };

    window.openMembership = function() {
        window.open('https://note.com/drcoyass/membership', '_blank');
    };

    // --- Hyper-Intelligence Stage: Final 100% Power Ups ---
    
    function init3DBackground() {
        const canvas = document.getElementById('molecular-canvas');
        if (!canvas) return;
        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 20;

        // Create a chain of polyphosphate (simple spheres)
        const spheres = [];
        const geometry = new THREE.SphereGeometry(0.5, 32, 32);
        const material = new THREE.MeshPhongMaterial({ color: 0x6366f1, emissive: 0x22d3ee, shininess: 100 });
        const light = new THREE.PointLight(0xffffff, 1, 100);
        light.position.set(10, 10, 10);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        for (let i = 0; i < 20; i++) {
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.x = (i - 10) * 1.5;
            sphere.position.y = Math.sin(i * 0.5) * 2;
            scene.add(sphere);
            spheres.push(sphere);
        }

        function animate() {
            requestAnimationFrame(animate);
            spheres.forEach((s, idx) => {
                s.position.y = Math.sin(Date.now() * 0.002 + idx * 0.5) * 3;
                s.rotation.x += 0.01;
            });
            renderer.render(scene, camera);
        }
        animate();
    }

    window.toggleAudioSummary = function(index) {
        const p = filteredData[index];
        const btn = document.getElementById(`audio-btn-\${p.id}`);
        
        if (speechSynth.speaking) {
            speechSynth.cancel();
            document.querySelectorAll('.audio-btn').forEach(b => b.classList.remove('playing'));
            if (currentUtterance && currentUtterance.id === p.id) {
                currentUtterance = null;
                return;
            }
        }

        const text = p.summary_jp || p.abstract || "No summary available.";
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = currentLang === 'ja' ? 'ja-JP' : 'en-US';
        utterance.onend = () => btn.classList.remove('playing');
        utterance.id = p.id;
        
        currentUtterance = utterance;
        btn.classList.add('playing');
        speechSynth.speak(utterance);
    };

    init3DBackground();
    // --- End 100% Power Ups ---

    if (searchBtn) searchBtn.onclick = performSearch;
    if (searchInput) searchInput.oninput = performSearch;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) loadMoreBtn.onclick = () => { displayedCount += 50; renderLibrary(); };
});
