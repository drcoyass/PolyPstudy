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
    
    const translations = {
        ja: {
            loadingText: "19,000件の論文データを同期中...",
            navResearch: "論文検索",
            navNetwork: "ネットワーク",
            navStory: "歴史",
            heroBadge: "分子インテリジェンス・ハブ",
            heroTitle: "ポリリン酸の起源を解き明かす<br><span class=\"highlight\">Poly-P</span>",
            heroDesc: "生命の起源から未来の再生医療まで。ライナス・ポーリングの分子整合医学からアーサー・コーンバーグの発見を経て、いま、ポリリン酸が知性の統合点となる。",
            statLive: "PUBMED ライブ同期",
            statTotalLabel: "累計論文数",
            statArchive: "研究アーカイブ",
            statEliteLabel: "同期済み精選データ",
            statHistory: "歴史的深度",
            statYearsLabel: "生命進化の歴史",
            btnKnowledge: "知識を探訪する",
            btnHistory: "歴史を紐解く",
            btnReport: "月次レポート (.pptx)",
            dashboardBadge: "インテリジェンス・ダッシュボード",
            dashboardTitle: "グローバル・インテリジェンス・ステータス",
            labelTrends: "研究トレンド（グローバル・アーカイブ）",
            captionTrends: "PubMed全論文（約2万件）の時代別推移",
            labelTopics: "トピック変遷（マスタータグ）",
            insightBadge: "専門医による推奨",
            insightTitle: "臨床の最前線：<span class=\"accent-text\">究極のホワイトニング</span>",
            insightSubtitle: "Prof.柴 & Dr.COYASSが提唱する、短鎖分割ポリリン酸による低刺激・高効率な臨床応用。",
            posterBadge: "学会発表知見",
            posterTitle: "短鎖分割ポリリン酸による<br>効果の高い痛みの少ないホワイトニング",
            labelChain: "鎖長",
            labelBleach: "漂白効果",
            valHigh: "高",
            labelSafety: "安全性",
            valUseful: "有用",
            posterConclusion: "<strong>【結論】</strong><br>短鎖分割ポリリン酸（平均鎖長14）と白金ナノコロイドを配合することで、低濃度でも高い漂白効果と再着色防止機能を実現。",
            btnViewEvidence: "エビデンスを詳しく見る ↗",
            expertLabel: "専門家による選定",
            productTitle: "短鎖分割ポリリン酸配合<br>プロフェッショナル・ホワイトニング",
            productDesc: "学会発表されたエビデンスに基づき、従来の「痛み」や「知覚過敏」を克服。臨床において最も効果が高く、痛みの少ない次世代のシステムです。",
            btnProductDetails: "製品詳細を確認する ↗",
            libTitle: "ナレッジ・<span class=\"highlight\">ライブラリ</span>",
            libSubtitle: "精微な検索とフィルタリングによる、統合された分子知見へのアクセス",
            labelTopicsFilter: "トピック",
            labelSourceFilter: "情報源",
            filterAll: "すべて",
            filterDental: "歯科",
            filterMedical: "医科",
            filterTop100: "TOP 100",
            filterDental100: "歯科 100",
            searchPlaceholder: "論文タイトル、著者、または分子キーワードで検索...",
            btnSearch: "検索",
            btnLoadMore: "研究データをさらに読み込む ▽",
            networkBadge: "研究エコシステム",
            networkTitle: "コラボレーション・<span class=\"highlight\">ネットワーク</span>",
            networkDesc: "ポリリン酸研究における世界的な研究機関の繋がり。",
            visualizingSynergy: "機関同士のシナジーを可視化中...",
            storyBadge: "分子のオデッセイ",
            storyTitle: "ポリリン酸：<span class=\"accent-text\">知性の軌跡</span>",
            storySubtitle: "発見から最新の再生医療まで、ポリリン酸が歩んだ分子進化の歴史。",
            event1Title: "ポリリン酸の発見と初期研究",
            event1Desc: "1890年代、L. Liebermannが酵母から初めてメタリン酸を同定。",
            event2Title: "コーンバーグによる金字塔",
            event2Desc: "ノーベル賞受賞者アーサー・コーンバーグがポリリン酸合成酵素（PPK）を発見。",
            event3Title: "哺乳類における役割の再定義",
            event3Desc: "2000年代、ヒトの血小板やミトコンドリアに大量のポリリン酸が貯蔵されていることを発見。",
            event4Title: "再生医療の最前線へ",
            event4Desc: "粘膜バリアの強化や骨再生など、次世代の医療応用が始まっています。",
            footerDesc: "分子生物学から臨床医学までを統合する、ポリリン酸研究のグローバル・アーカイブ",
            footerCreditHP: "HP作成・監修",
            footerAssoc: "分割ポリリン酸研究会",
            footerCreditOps: "協力 / 運営",
            footerCopyright: "分割ポリリン酸研究会. All Rights Reserved."
        },
        en: {
            loadingText: "Syncing 19,000 research records...",
            navResearch: "Research",
            navNetwork: "Network",
            navStory: "Story",
            heroBadge: "Molecular Intelligence Hub",
            heroTitle: "Unlocking the Origins of <br><span class=\"highlight\">Poly-P</span>",
            heroDesc: "From the origins of life to future regenerative medicine. Following the footsteps of Linus Pauling and Arthur Kornberg, polyphosphate now becomes the nexus of intelligence.",
            statLive: "PUBMED LIVE SYNC",
            statTotalLabel: "Total Papers",
            statArchive: "Research Archive",
            statEliteLabel: "Curated Data",
            statHistory: "Historical Depth",
            statYearsLabel: "Evolutionary Timeline",
            btnKnowledge: "Explore Wisdom",
            btnHistory: "Unlock History",
            btnReport: "Monthly Report (.pptx)",
            dashboardBadge: "Intelligence Dashboard",
            dashboardTitle: "Global Intelligence Status",
            labelTrends: "Research Trends (Global Archive)",
            captionTrends: "PubMed historical distribution (Approx. 20,000 papers)",
            labelTopics: "Topic Evolution (Master Tags)",
            insightBadge: "Professional Recommendation",
            insightTitle: "Frontiers of Clinical Practice: <span class=\"accent-text\">Ultimate Whitening</span>",
            insightSubtitle: "High-efficiency clinical application of short-chain polyphosphate proposed by Prof. Shiba & Dr. COYASS.",
            posterBadge: "Academic Evidence",
            posterTitle: "High-Efficiency, Low-Sensitivity Whitening <br>via Short-Chain Polyphosphate",
            labelChain: "Chain Length",
            labelBleach: "Bleaching",
            valHigh: "High",
            labelSafety: "Safety",
            valUseful: "Useful",
            posterConclusion: "<strong>[Conclusion]</strong><br>Formulation of short-chain polyphosphate (avg length 14) and platinum nanocolloid achieves high whitening effect and prevents re-staining even at low concentrations.",
            btnViewEvidence: "View Evidence Poster ↗",
            expertLabel: "Selection by Academic Experts",
            productTitle: "Professional Whitening with <br>Short-Chain Polyphosphate",
            productDesc: "Overcoming traditional pain and sensitivity based on evidence. The most effective and painless next-generation system in clinical practice.",
            btnProductDetails: "View Product Details ↗",
            libTitle: "Knowledge <span class=\"highlight\">Library</span>",
            libSubtitle: "Access to integrated molecular insights through precise search and filtering",
            labelTopicsFilter: "TOPICS",
            labelSourceFilter: "SOURCE",
            filterAll: "ALL",
            filterDental: "DENTAL",
            filterMedical: "MEDICAL",
            filterTop100: "TOP 100",
            filterDental100: "DENTAL 100",
            searchPlaceholder: "Search by paper title, authors, or molecular keywords...",
            btnSearch: "SEARCH",
            btnLoadMore: "LOAD MORE RESEARCH DATA ▽",
            networkBadge: "Research Ecosystem",
            networkTitle: "Collaboration <span class=\"highlight\">Network</span>",
            networkDesc: "Visualizing global institutional synergy in polyphosphate research.",
            visualizingSynergy: "Visualizing Institutional Synergy...",
            storyBadge: "Molecular Odyssey",
            storyTitle: "Poly-P: <span class=\"accent-text\">Trace of Intelligence</span>",
            storySubtitle: "The history of molecular evolution from discovery to modern regenerative medicine.",
            event1Title: "Discovery & Early Studies",
            event1Desc: "1890s: L. Liebermann first identified metaphosphate from yeast.",
            event2Title: "Kornberg's Milestone",
            event2Desc: "Nobel Laureate Arthur Kornberg discovered Polyphosphate Kinase (PPK).",
            event3Title: "Redefining Mammalian Roles",
            event3Desc: "2000s: Massive stores of polyphosphate discovered in human platelets and mitochondria.",
            event4Title: "Toward Regenerative Medicine",
            event4Desc: "Next-generation applications like mucosal barrier enhancement and bone regeneration are commencing.",
            footerDesc: "A global archive for polyphosphate research integrating biology and medicine.",
            footerCreditHP: "HP Creation / Supervision",
            footerAssoc: "The Society for Polyphosphate Study",
            footerCreditOps: "Collaboration / Operations",
            footerCopyright: "The Society for Polyphosphate Study. All Rights Reserved."
        }
    };

    function updateLanguage() {
        const t = translations[currentLang];
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
                el.innerHTML = t[key];
            }
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (t[key]) {
                el.setAttribute('placeholder', t[key]);
            }
        });
        
        // 言語ボタンの表示更新
        langToggle.textContent = currentLang === 'ja' ? 'EN' : '日本語';
        
        // ライブラリの再描画
        displayedCount = 50;
        renderLibrary();
    }
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

    // --- Event Listeners & Initialization ---
    langToggle.addEventListener('click', () => {
        currentLang = currentLang === 'ja' ? 'en' : 'ja';
        updateLanguage();
    });

    // 初期起動時の言語同期
    updateLanguage();

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

        // 言語に応じた表示設定
        const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
        const displayAuthors = (p.authors || "Academic Record");
        const abstractLabel = currentLang === 'ja' ? '研究抄録' : 'RESEARCH ABSTRACT';
        const sourceLabel = currentLang === 'ja' ? 'ソースを表示 ↗' : 'VIEW SOURCE ↗';
        const pdfLabel = currentLang === 'ja' ? 'PDFを検索 📋' : 'SEARCH PDF 📋';
        
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

    window.filterByYear = function(year) {
        if (!year) return;
        if (searchInput) {
            // "2022" のように検索窓に入れ、即座に検索を実行
            searchInput.value = year;
            performSearch();
            const papersSection = document.getElementById('papers');
            if (papersSection) papersSection.scrollIntoView({ behavior: 'smooth' });
        }
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

    window.openPosterModal = function() {
        const modal = document.getElementById('posterModal');
        const modalBody = document.getElementById('posterModalBody');
        const actualImg = document.getElementById('actualPosterImg');
        const isFallback = document.querySelector('.poster-container').classList.contains('poster-fallback');
        
        if (!modal || !modalBody) return;

        if (isFallback) {
            // 画像がない場合の詳細デジタルパネル
            modalBody.innerHTML = `
                <div style="padding: 2rem; color: #fff;">
                    <h2 style="color: var(--accent-cyan); margin-bottom: 2rem;">学会発表データ詳細エビデンス</h2>
                    <div class="glass-card" style="padding: 2rem; margin-bottom: 2rem; background: rgba(34, 211, 238, 0.05); border: 1px solid var(--accent-cyan);">
                        <h3 style="color: #fff; margin-bottom: 1rem;">短鎖分割ポリリン酸による効果の高い痛みの少ないホワイトニング</h3>
                        <p style="color: var(--text-secondary); line-height: 1.8;">
                            <strong>【目的および背景】</strong><br>
                            本研究では、過酸化水素および過酸化尿素に短鎖分割ポリリン酸（平均鎖長14）を添加することで、低濃度での漂白効率および再着色防止効果を検証した。
                        </p>
                        <p style="color: var(--text-secondary); line-height: 1.8; margin-top: 1rem;">
                            <strong>【結果】</strong><br>
                            短鎖分割ポリリン酸と白金ナノコロイドの相乗効果により、低濃度の漂白剤でも高濃度と同等の漂白効果を実現。また、歯面コーティング作用により、施術後の再着色が物理的に阻害されることが確認された。
                        </p>
                    </div>
                    <div style="text-align: center;">
                        <a href="https://www.smile-us.com/sub1-371.html" target="_blank" class="primary-btn">製品の詳細ページへ ↗</a>
                    </div>
                </div>
            `;
        } else {
            // 画像がある場合の高精細表示
            modalBody.innerHTML = `
                <div style="text-align: center;">
                    <img src="${actualImg.src}" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    <p style="margin-top: 1.5rem; color: var(--text-secondary);">Academic Conference Poster: Scientific Evidence Analysis</p>
                </div>
            `;
        }

        modal.style.display = "block";
        modal.style.zIndex = "100000";
        document.body.style.overflow = "hidden";
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
            renderTopicCloud(data);
            performSearch();
        })
        .catch(err => {
            console.error("Data Load Error:", err);
            finishLoading(loadingInterval);
        });

    function performSearch() {
        if (!searchInput) return;
        let query = searchInput.value.toLowerCase().trim();
        displayedCount = 50;

        if (!query) {
            filteredData = [...papersData];
            renderLibrary();
            return;
        }

        const isYearQuery = /^\d{4}$/.test(query);
        const isWhiteningTheme = query.includes('ホワイトニング') || query.includes('bleaching') || query.includes('whitening');
        
        // 歯科専門分野のブーストキーワードとノイズワード
        const dentalBoost = ['tooth', 'teeth', 'dental', 'enamel', 'dentin', 'stain', 'dentistry', '歯科', '歯', 'エナメル'];
        const industryNoise = ['coral', 'marine', 'algae', 'ship', 'pulp', 'textile', 'paper', 'waste', 'blood cell'];

        filteredData = papersData.map(p => {
            let score = 0;
            const fullText = [
                p.title, p.jp_title, p.abstract, p.summary_jp, 
                p.authors, ...(p.tags || [])
            ].filter(Boolean).join(' ').toLowerCase();

            const titleText = ((p.title || "") + " " + (p.jp_title || "")).toLowerCase();

            if (fullText.includes(query)) {
                score += 100;
                if (titleText.includes(query)) score += 150;

                if (isWhiteningTheme) {
                    const hasDentalContext = dentalBoost.some(kw => fullText.includes(kw));
                    const hasNoiseContext = industryNoise.some(kw => fullText.includes(kw));
                    if (hasDentalContext) score += 400; 
                    if (hasNoiseContext) score -= 500; 
                }
                const year = parseInt(p.year || (p.date ? p.date.substring(0,4) : "0"));
                if (year >= 2020) score += 20;
            }

            if (isYearQuery) {
                const pYear = p.year || (p.date ? p.date.substring(0,4) : "");
                if (pYear === query) score += 10000;
            }

            p._searchScore = score;
            return p;
        }).filter(p => p._searchScore > 0)
          .sort((a, b) => b._searchScore - a._searchScore);

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
        
        const renderStep = 50;
        const currentSlice = filteredData.slice(0, displayedCount);
        
        if (displayedCount === renderStep) {
            paperIndexList.innerHTML = '';
        }

        if (filteredData.length === 0) {
            paperIndexList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>該当する知見が見つかりませんでした</h3>
                    <p>キーワードを少し変えるか、インプラント・歯科・骨再生などの主要カテゴリから探索を広げてみてください。</p>
                </div>
            `;
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) loadMoreBtn.style.display = 'none';
            return;
        }

        const fragment = document.createDocumentFragment();
        const startIdx = displayedCount - renderStep;
        const itemsToRender = currentSlice.slice(Math.max(0, startIdx));

        itemsToRender.forEach((p, i) => {
            const actualIndex = Math.max(0, startIdx) + i;
            const li = document.createElement('div');
            li.className = 'knowledge-card';
            li.onclick = (e) => window.openPaperModalFromIndex(actualIndex, e);

            // 年度取得の堅牢化 (year, date, または PMID からの推測)
            let displayYear = p.year || (p.date ? p.date.substring(0,4) : '---');
            if (displayYear === '---' && p.id && p.id.length > 5) {
                // PMID等から年代を推測するロジックがあればここで補完
            }

            const displayTitle = (currentLang === 'ja' && p.jp_title) ? p.jp_title : p.title;
            const displayAuthors = (p.authors || "Academic Record");
            const sourceUrl = getPaperSourceUrl(p).replace(/'/g, "\\'");
            
            const btnAbstractLabel = currentLang === 'ja' ? '概要表示' : 'ABSTRACT';
            const btnSourceLabel = currentLang === 'ja' ? 'ソース ↗' : 'SOURCE ↗';

            li.innerHTML = `
                <div class="card-side-info">
                    <div class="year-badge">${displayYear}</div>
                    <div class="card-tags-v">
                        ${(p.tags || []).slice(0,2).map(t => {
                            let tagText = t;
                            if (currentLang === 'en') {
                                if (t === '歯科') tagText = 'DENTAL';
                                if (t === 'インプラント') tagText = 'IMPLANT';
                                if (t === '再生医療') tagText = 'REGEN';
                            }
                            return `<span class="tag-chip">${tagText}</span>`;
                        }).join('')}
                    </div>
                </div>
                <div class="card-main-content">
                    <div class="card-header-row">
                        <span class="source-badge source-pubmed">PUBMED</span>
                        <span class="pmid-small">PMID: ${p.id}</span>
                    </div>
                    <div class="card-title">${displayTitle}</div>
                    <div class="card-authors-row">${displayAuthors}</div>
                    <div class="card-abstract-preview">
                        ${(currentLang === 'ja' && p.summary_jp ? p.summary_jp : (p.abstract || "")).substring(0, 200)}...
                    </div>
                </div>
                <div class="card-actions-v">
                    <button class="primary-btn abstract-btn" onclick="window.openPaperModalFromIndex(${actualIndex}, event)">
                        <span class="btn-icon">📄</span> ${btnAbstractLabel}
                    </button>
                    <button class="secondary-btn source-jump-btn" onclick="window.openPaperSource('${sourceUrl}', event)">
                        ${btnSourceLabel}
                    </button>
                </div>
            `;
            fragment.appendChild(li);
        });
        
        paperIndexList.appendChild(fragment);

        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = (displayedCount < filteredData.length) ? 'block' : 'none';
        }
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
            bar.style.cursor = 'pointer';
            bar.onclick = () => window.filterByYear(y);
            
            bar.innerHTML = `
                <span class="trend-bar-value">${stats[y].toLocaleString()}</span>
                <span class="trend-bar-inner">${y}</span>
            `;
            trendChart.appendChild(bar);
        });
    }

    function renderTopicCloud(dataObj) {
        const topicCloud = document.getElementById('topicCloud');
        if (!topicCloud) return;
        
        let counts = dataObj.global_topic_stats;
        if (!counts) {
            counts = {};
            const papers = dataObj.papers || [];
            papers.forEach(p => { (p.tags || []).forEach(t => counts[t] = (counts[t] || 0) + 1); });
        }
        
        const sorted = Object.keys(counts).sort((a,b) => counts[b] - counts[a]).slice(0, 15);
        topicCloud.innerHTML = sorted.map(t => `
            <div class="topic-item" onclick="window.filterByTag('${t}')">
                <span class="topic-name">${t}</span>
                <span class="topic-count">${counts[t].toLocaleString()}</span>
            </div>
        `).join('');
    }

    // --- Global Nav Actions ---
    window.filterByTag = function(tag) {
        if (!searchInput) return;
        searchInput.value = tag;
        performSearch();
        const target = document.getElementById('papers');
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    };

    window.filterByYear = function(year) {
        if (!searchInput) return;
        searchInput.value = year;
        performSearch();
        const target = document.getElementById('papers');
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    };

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
