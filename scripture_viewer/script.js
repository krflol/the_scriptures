// This script is now injected into index.html by build.py
// The `scriptureData` variable is globally available in the <script> tag.

document.addEventListener('DOMContentLoaded', () => {
    const navigationTree = document.getElementById('navigation-tree');
    const chapterTitle = document.getElementById('chapter-title');
    const chapterContent = document.getElementById('chapter-content');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    let flatData = [];
    let docIndex = [];
    let invertedIndex = Object.create(null); // term -> Array of {doc, tf}
    let docLengths = [];
    let avgDocLen = 0;
    let vocabulary = [];
    const BM25_K1 = 1.5;
    const BM25_B = 0.75;
    const STOPWORDS = new Set([
        'the','and','of','to','in','a','that','is','it','for','on','with','as','be','are','was','were','by','an','at','from','or','this','which','but','not','have','has','had','his','her','their','its','he','she','they','we','you','i','them','these','those'
    ]);

    // Indexes for navigation and canonical search
    const bookIndex = new Map(); // bookName -> { division, subsection: string|null, chapters: Set }
    const aliasToBook = new Map(); // alias -> bookName

    function stripHtml(html) {
        return html.replace(/<[^>]+>/g, ' ');
    }

    function tokenize(text) {
        return text
            .toLowerCase()
            .replace(/[^a-z0-9\u00C0-\u024F\s]/g, ' ')
            .split(/\s+/)
            .filter(t => t && !STOPWORDS.has(t));
    }

    function buildSearchIndex() {
        docIndex = flatData;
        invertedIndex = Object.create(null);
        docLengths = new Array(docIndex.length);
        let totalLen = 0;

        for (let i = 0; i < docIndex.length; i++) {
            const d = docIndex[i];
            const plain = stripHtml(`${d.book} ${d.text}`);
            const tokens = tokenize(plain);
            docLengths[i] = tokens.length || 1;
            totalLen += docLengths[i];

            const tfMap = Object.create(null);
            for (const tok of tokens) {
                tfMap[tok] = (tfMap[tok] || 0) + 1;
            }
            for (const tok in tfMap) {
                if (!invertedIndex[tok]) invertedIndex[tok] = [];
                invertedIndex[tok].push({ doc: i, tf: tfMap[tok] });
            }
        }
        avgDocLen = totalLen / docIndex.length;
        vocabulary = Object.keys(invertedIndex);
    }

    // --- Helpers for nested divisions and canonical sorting ---
    function isChaptersObject(obj) {
        if (!obj || typeof obj !== 'object') return false;
        for (const k in obj) {
            if (Array.isArray(obj[k])) return true;
            break;
        }
        return false;
    }

    function sortedKeys(obj) {
        return Object.keys(obj).sort((a, b) => {
            const na = parseInt(String(a).split(' - ')[0], 10);
            const nb = parseInt(String(b).split(' - ')[0], 10);
            const aNum = Number.isFinite(na);
            const bNum = Number.isFinite(nb);
            if (aNum && bNum) return na - nb;
            if (aNum) return -1;
            if (bNum) return 1;
            return a.localeCompare(b);
        });
    }

    function forEachBook(cb) {
        for (const division of Object.keys(scriptureData)) {
            const divObj = scriptureData[division];
            const firstKey = Object.keys(divObj)[0];
            if (firstKey && isChaptersObject(divObj[firstKey])) {
                // Books directly under division
                for (const bookName of sortedKeys(divObj)) {
                    cb(division, null, bookName, divObj[bookName]);
                }
            } else {
                // Subsections under division
                for (const subsection of Object.keys(divObj)) {
                    const subObj = divObj[subsection];
                    for (const bookName of sortedKeys(subObj)) {
                        cb(division, subsection, bookName, subObj[bookName]);
                    }
                }
            }
        }
    }

    function bm25Search(query, limit = 100) {
        const qTokens = Array.from(new Set(tokenize(query)));
        if (qTokens.length === 0) return [];

        const N = docIndex.length;
        const scores = new Map();

        for (const tok of qTokens) {
            let terms = invertedIndex[tok] ? [tok] : [];
            // Prefix expansion for partial tokens (length >= 2)
            if (tok.length >= 2) {
                const pref = tok;
                const matches = vocabulary.filter(t => t.startsWith(pref));
                // Avoid duplicates
                for (const t of matches) if (!terms.includes(t)) terms.push(t);
            }
            if (terms.length === 0) continue;

            for (const term of terms) {
                const postings = invertedIndex[term];
                if (!postings || postings.length === 0) continue;
                const n = postings.length;
                const idf = Math.log((N - n + 0.5) / (n + 0.5) + 1);
                for (const { doc, tf } of postings) {
                    const dl = docLengths[doc];
                    const denom = tf + BM25_K1 * (1 - BM25_B + BM25_B * (dl / avgDocLen));
                    const score = idf * (tf * (BM25_K1 + 1)) / denom;
                    scores.set(doc, (scores.get(doc) || 0) + score);
                }
            }
        }

        const ranked = Array.from(scores.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([doc]) => docIndex[doc]);
        return ranked;
    }

    // --- Data Initialization ---
    function initialize() {
        if (typeof scriptureData === 'undefined' || Object.keys(scriptureData).length === 0) {
            console.error("Scripture data is missing!");
            chapterContent.innerHTML = `<p>Error: Scripture data not found. Please re-run the build script: <code>python scripture_viewer/build.py</code></p>`;
            return;
        }
        flattenData();
        buildIndexesForBooks();
        buildSearchIndex();
        buildNavigation();
        injectNavSearch();
    }

    function flattenData() {
        forEachBook((division, subsection, bookName, chaptersObj) => {
            const chapterKeys = Object.keys(chaptersObj);
            bookIndex.set(bookName, { division, subsection, chapters: new Set(chapterKeys) });
            for (const chapterNum of chapterKeys) {
                const verses = chaptersObj[chapterNum];
                if (Array.isArray(verses)) {
                    verses.forEach(verse => {
                        flatData.push({
                            division,
                            subsection,
                            book: bookName,
                            chapter: chapterNum,
                            ...verse
                        });
                    });
                }
            }
        });
    }

    function buildIndexesForBooks() {
        aliasToBook.clear();
        for (const [bookName, meta] of bookIndex.entries()) {
            const commonMatch = bookName.match(/\(([^)]+)\)/);
            const common = (commonMatch ? commonMatch[1] : bookName).toLowerCase().trim();
            addBookAliases(common, bookName);
            // Also add 3-letter abbreviation of the common name (last token)
            const parts = common.split(/\s+/);
            const last = parts[parts.length - 1] || common;
            addIfEmpty(last.slice(0, 3), bookName);
            // Add no-space variant
            addIfEmpty(common.replace(/\s+/g, ''), bookName);
        }
        // Helper: prefer first assignment to keep deterministic defaults
        function addIfEmpty(alias, bookName) {
            if (!alias) return;
            if (!aliasToBook.has(alias)) aliasToBook.set(alias, bookName);
        }
        function addBookAliases(common, bookName) {
            addIfEmpty(common, bookName);
            addIfEmpty(common.replace(/\s+/g, ''), bookName);
            const m = common.match(/^(\d)\s+(.+)$/);
            if (m) {
                const num = m[1];
                const rest = m[2];
                addIfEmpty(`${num} ${rest}`, bookName);
                addIfEmpty(`${num}${rest.replace(/\s+/g, '')}`, bookName);
                addIfEmpty(`${num}${(rest.split(/\s+/)[0] || rest).slice(0, 3)}`, bookName); // 1tim
                addIfEmpty(rest, bookName); // timothy => defaults to 1 book if multiple
                addIfEmpty((rest.split(/\s+/)[0] || rest).slice(0, 3), bookName); // tim
            } else {
                const abbr = (common.split(/\s+/)[0] || common).slice(0, 3);
                addIfEmpty(abbr, bookName);
            }
        }
    }

    // --- Book display helper (prefix + Hebrew + Common) ---
    function parseBookDisplay(bookName) {
        const prefixMatch = bookName.match(/^\s*(\d+)\s*-\s*/);
        const prefix = prefixMatch ? prefixMatch[1] : null;
        const base = bookName.replace(/^\s*\d+\s*-\s*/, '').trim();
        const commonMatch = base.match(/\(([^)]+)\)/);
        const hebrew = base.replace(/\s*\(.*\)\s*$/, '').trim();
        const common = commonMatch ? commonMatch[1].trim() : null;
        return { prefix, hebrew, common };
    }

    // --- Navigation ---
    function buildNavigation() {
        const ul = document.createElement('ul');
        for (const divName of Object.keys(scriptureData)) {
            const divLi = document.createElement('li');
            const divHeader = document.createElement('div');
            divHeader.textContent = divName;
            divHeader.style.fontWeight = 'bold';
            divHeader.style.cursor = 'pointer';
            const divUl = document.createElement('ul');
            divUl.style.display = 'none';
            divHeader.addEventListener('click', () => {
                divUl.style.display = divUl.style.display === 'none' ? '' : 'none';
            });

            const divObj = scriptureData[divName];
            const firstKey = Object.keys(divObj)[0];
            const hasSubsections = firstKey && !isChaptersObject(divObj[firstKey]);

            if (hasSubsections) {
                for (const subsection of Object.keys(divObj)) {
                    const subLi = document.createElement('li');
                    const subHeader = document.createElement('div');
                    subHeader.textContent = subsection;
                    subHeader.style.cursor = 'pointer';
                    const booksUl = document.createElement('ul');
                    booksUl.style.display = 'none';
                    subHeader.addEventListener('click', () => {
                        booksUl.style.display = booksUl.style.display === 'none' ? '' : 'none';
                    });
                    for (const bookName of sortedKeys(divObj[subsection])) {
                        const bookLi = buildBookNode(divName, bookName, divObj[subsection][bookName], subsection);
                        booksUl.appendChild(bookLi);
                    }
                    subLi.appendChild(subHeader);
                    subLi.appendChild(booksUl);
                    divUl.appendChild(subLi);
                }
            } else {
                for (const bookName of sortedKeys(divObj)) {
                    const bookLi = buildBookNode(divName, bookName, divObj[bookName]);
                    divUl.appendChild(bookLi);
                }
            }

            divLi.appendChild(divHeader);
            divLi.appendChild(divUl);
            ul.appendChild(divLi);
        }
        navigationTree.innerHTML = '';
        navigationTree.appendChild(ul);
    }

    function buildBookNode(divName, bookName, chaptersObj, subsectionName = null) {
        const bookLi = document.createElement('li');
        bookLi.className = 'book-item';
        const bookHeader = document.createElement('div');
        bookHeader.textContent = bookName;
        bookHeader.style.cursor = 'pointer';
        const chapterUl = document.createElement('ul');
        chapterUl.style.display = 'none';
        bookHeader.addEventListener('click', () => {
            chapterUl.style.display = chapterUl.style.display === 'none' ? '' : 'none';
        });
        for (const chapterNum of Object.keys(chaptersObj).sort((a,b)=>Number(a)-Number(b))) {
            const chapterLi = document.createElement('li');
            chapterLi.className = 'nav-item';
            chapterLi.textContent = `Chapter ${chapterNum}`;
            chapterLi.dataset.division = divName;
            chapterLi.dataset.book = bookName;
            chapterLi.dataset.chapter = chapterNum;
            if (subsectionName) chapterLi.dataset.subsection = subsectionName;
            chapterLi.addEventListener('click', handleNavClick);
            chapterUl.appendChild(chapterLi);
        }
        bookLi.appendChild(bookHeader);
        bookLi.appendChild(chapterUl);
        return bookLi;
    }

    function handleNavClick(event) {
        const { division, book, chapter, subsection } = event.target.dataset;
        displayChapter(division, book, chapter, subsection || null);

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        event.target.classList.add('active');
    }

    function injectNavSearch() {
        const container = navigationTree.parentElement;
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'nav-search-input';
        input.placeholder = 'Filter books or try gen1:1, 1tim 2:5';
        input.style.width = 'calc(100% - 20px)';
        input.style.padding = '8px';
        input.style.marginBottom = '8px';
        input.style.border = '1px solid #ccc';
        input.style.borderRadius = '4px';
        container.insertBefore(input, navigationTree);

        input.addEventListener('input', () => {
            const q = input.value.trim();
            if (tryReferenceJump(q)) return;
            filterNavigation(q.toLowerCase());
        });
    }

    function filterNavigation(q) {
        const books = navigationTree.querySelectorAll('.book-item');
        books.forEach(bookLi => {
            const header = bookLi.firstChild;
            const match = header.textContent.toLowerCase().includes(q);
            bookLi.style.display = match || !q ? '' : 'none';
            // Expand matched books
            if (match && q) {
                const chapterUl = bookLi.querySelector('ul');
                if (chapterUl) chapterUl.style.display = '';
                // Ensure division is expanded
                const divUl = bookLi.parentElement;
                if (divUl && divUl.style.display === 'none') divUl.style.display = '';
            }
        });
    }

    // --- Content Display ---
    function getVerses(division, book, chapter, subsection = null) {
        if (subsection) {
            return scriptureData[division]?.[subsection]?.[book]?.[chapter];
        }
        // If not provided, try to locate the book in any subsection
        const divObj = scriptureData[division];
        if (!divObj) return null;
        if (divObj[book]?.[chapter]) return divObj[book][chapter];
        for (const sub of Object.keys(divObj)) {
            if (divObj[sub]?.[book]?.[chapter]) return divObj[sub][book][chapter];
        }
        return null;
    }

    function displayChapter(division, book, chapter, subsection = null) {
        const verses = getVerses(division, book, chapter, subsection);
        if (!verses) return;

        const bd = parseBookDisplay(book);
        chapterTitle.textContent = `${bd.prefix ? bd.prefix + ' - ' : ''}${bd.hebrew}${bd.common ? ' (' + bd.common + ')' : ''} - Chapter ${chapter}`;
        chapterContent.innerHTML = '';

        verses.forEach(verse => {
            const p = document.createElement('p');
            p.className = 'verse';
            p.id = verse.id;

            const span = document.createElement('span');
            span.className = 'verse-number';
            span.textContent = verse.verse;

            // Render the verse text as HTML
            const textNode = document.createElement('span');
            textNode.innerHTML = verse.text; // Use innerHTML to parse links

            p.appendChild(span);
            p.appendChild(textNode);
            chapterContent.appendChild(p);
        });
    }

    // --- Canonical Reference Parsing ---
    function tryReferenceJump(rawQuery) {
        const q = (rawQuery || '').trim().toLowerCase();
        if (!q) return false;

        // Patterns:
        // 1) book chapter:verse e.g., gen 1:1, timothy2:5
        let m = q.match(/^([a-z]+)\s*(\d+)\s*:\s*(\d+)$/);
        if (!m) {
            // 2) numeric-leading book e.g., 1tim 2:5, 2 tim 3:16
            m = q.match(/^(\d)\s*([a-z]+)\s*(\d+)\s*:\s*(\d+)$/);
            if (m) {
                const num = m[1];
                const word = m[2];
                const chapter = m[3];
                const verse = m[4];
                const candidates = [
                    `${num} ${word}`,
                    `${num}${word}`,
                    word
                ];
                for (const key of candidates) {
                    const bookName = aliasToBook.get(key);
                    if (bookName) return jumpTo(bookName, chapter, verse);
                }
                return false;
            }
        } else {
            const word = m[1];
            const chapter = m[2];
            const verse = m[3];
            const bookName = aliasToBook.get(word) || aliasToBook.get(word.replace(/\s+/g, ''));
            if (bookName) return jumpTo(bookName, chapter, verse);
            return false;
        }
        return false;
    }

    // Parse structured queries for book or book+chapter (no verse)
    function parseStructuredQuery(rawQuery) {
        const q = (rawQuery || '').trim().toLowerCase();
        if (!q) return null;

        // e.g., "gen 1", "genesis 3", "1tim 2", "2 timothy 1"
        let m = q.match(/^([a-z][a-z\s']+?)\s+(\d+)$/);
        if (!m) {
            m = q.match(/^(\d)\s*([a-z][a-z\s']+?)\s*(\d+)$/);
            if (m) {
                const num = m[1];
                const name = m[2].replace(/\s+/g, ' ');
                const chapter = m[3];
                const candidates = [
                    `${num} ${name}`,
                    `${num}${name.replace(/\s+/g, '')}`,
                    name
                ];
                for (const key of candidates) {
                    const bookName = aliasToBook.get(key);
                    if (bookName) return { bookName, chapter };
                }
                return null;
            }
        }
        if (m) {
            const name = m[1].replace(/\s+/g, ' ');
            const chapter = m[2];
            const bookName = aliasToBook.get(name) || aliasToBook.get(name.replace(/\s+/g, ''));
            if (bookName) return { bookName, chapter };
        }

        // book-only, try exact alias first, then inclusive match across aliases
        const exact = aliasToBook.get(q) || aliasToBook.get(q.replace(/\s+/g, ''));
        if (exact) return { bookName: exact };

        // Fuzzy contains: choose first alias that contains q
        for (const [alias, bname] of aliasToBook.entries()) {
            if (alias.includes(q)) {
                return { bookName: bname };
            }
        }
        return null;
    }

    function renderBookChapterResults(bookName, chapterIfAny) {
        const meta = bookIndex.get(bookName);
        if (!meta) return false;
        const { division, subsection } = meta;
        const chapters = Array.from(meta.chapters).map(n => Number(n)).sort((a,b)=>a-b);
        searchResults.innerHTML = '';

        // If a specific chapter provided and exists, jump directly
        if (chapterIfAny && meta.chapters.has(String(chapterIfAny))) {
            displayChapter(division, bookName, String(chapterIfAny), subsection || null);
            return true;
        }

        // Otherwise, present a list of chapters for the selected book
        const header = document.createElement('div');
        header.className = 'search-result-item';
        header.style.fontWeight = 'bold';
        const bd = parseBookDisplay(bookName);
        header.textContent = `${bd.prefix ? bd.prefix + ' - ' : ''}${bd.hebrew}${bd.common ? ' (' + bd.common + ')' : ''}`;
        searchResults.appendChild(header);

        chapters.forEach(ch => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.addEventListener('click', () => displayChapter(division, bookName, String(ch), subsection || null));

            const loc = document.createElement('div');
            loc.className = 'location';
            loc.textContent = `${bd.hebrew}${bd.common ? ' (' + bd.common + ')' : ''} ${ch}`;

            // Show first verse as a snippet if available
            const verses = scriptureData[division]?.[bookName]?.[String(ch)] || [];
            const first = verses[0];
            const snippet = document.createElement('div');
            snippet.className = 'text-snippet';
            snippet.innerHTML = first ? first.text : '';

            item.appendChild(loc);
            item.appendChild(snippet);
            searchResults.appendChild(item);
        });
        return true;
    }

    function jumpTo(bookName, chapter, verse) {
        const meta = bookIndex.get(bookName);
        if (!meta) return false;
        const { division, subsection } = meta;
        const verses = getVerses(division, bookName, chapter, subsection || null);
        if (!verses) return false;
        displayChapter(division, bookName, chapter, subsection || null);
        setTimeout(() => {
            const verseElement = document.getElementById(`v${verse}`);
            if (verseElement) {
                verseElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                verseElement.style.backgroundColor = '#fff2a8';
                setTimeout(() => { verseElement.style.backgroundColor = '' }, 2000);
            }
        }, 100);
        return true;
    }

    // --- Search ---
    function handleSearch() {
        const raw = searchInput.value;
        const query = raw.toLowerCase();
        searchResults.innerHTML = '';

        // 1) Full canonical reference (book chap:verse)
        if (tryReferenceJump(raw)) {
            return;
        }

        // 2) Book-only or Book+Chapter (no verse) search
        const structured = parseStructuredQuery(raw);
        if (structured) {
            const { bookName, chapter } = structured;
            if (renderBookChapterResults(bookName, chapter)) return;
        }

        // 3) Keyword semantic search
        if (query.length < 2) return;

        const results = bm25Search(query, 100);

        results.slice(0, 100).forEach(result => {
            const div = document.createElement('div');
            div.className = 'search-result-item';
            div.addEventListener('click', () => {
                displayChapter(result.division, result.book, result.chapter, result.subsection || null);
                setTimeout(() => {
                    const verseElement = document.getElementById(result.id);
                    if (verseElement) {
                        verseElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        verseElement.style.backgroundColor = '#fff2a8';
                        setTimeout(() => { verseElement.style.backgroundColor = '' }, 2000);
                    }
                }, 100);
            });

            const location = document.createElement('div');
            location.className = 'location';
            const bd2 = parseBookDisplay(result.book);
            location.textContent = `${bd2.prefix ? bd2.prefix + ' - ' : ''}${bd2.hebrew}${bd2.common ? ' (' + bd2.common + ')' : ''} ${result.chapter}:${result.verse}`;

            const snippet = document.createElement('div');
            snippet.className = 'text-snippet';
            const tokens = tokenize(query);
            let highlightedText = result.text;
            for (const t of tokens) {
                // Highlight full token and prefix matches at word boundaries
                const re = new RegExp(`(\\b${t}[A-Za-z0-9\u00C0-\u024F]*)`, 'gi');
                highlightedText = highlightedText.replace(re, '<strong>$1</strong>');
            }
            snippet.innerHTML = highlightedText;

            div.appendChild(location);
            div.appendChild(snippet);
            searchResults.appendChild(div);
        });
    }

    searchInput.addEventListener('input', handleSearch);

    // --- Initial Load ---
    initialize();
});
