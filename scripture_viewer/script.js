// This script is now injected into index.html by build.py
// The `scriptureData` variable is globally available in the <script> tag.

document.addEventListener('DOMContentLoaded', () => {
    const navigationTree = document.getElementById('navigation-tree');
    const chapterTitle = document.getElementById('chapter-title');
    const chapterContent = document.getElementById('chapter-content');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    let flatData = [];

    // --- Data Initialization ---
    function initialize() {
        if (typeof scriptureData === 'undefined' || Object.keys(scriptureData).length === 0) {
            console.error("Scripture data is missing!");
            chapterContent.innerHTML = `<p>Error: Scripture data not found. Please re-run the build script: <code>python scripture_viewer/build.py</code></p>`;
            return;
        }
        flattenData();
        buildNavigation();
    }

    function flattenData() {
        for (const divName in scriptureData) {
            for (const bookName in scriptureData[divName]) {
                for (const chapterNum in scriptureData[divName][bookName]) {
                    const verses = scriptureData[divName][bookName][chapterNum];
                    if (Array.isArray(verses)) {
                        verses.forEach(verse => {
                            flatData.push({
                                division: divName,
                                book: bookName,
                                chapter: chapterNum,
                                ...verse
                            });
                        });
                    }
                }
            }
        }
    }

    // --- Navigation ---
    function buildNavigation() {
        const ul = document.createElement('ul');
        for (const divName in scriptureData) {
            const divLi = document.createElement('li');
            divLi.textContent = divName;
            const bookUl = document.createElement('ul');
            for (const bookName in scriptureData[divName]) {
                const bookLi = document.createElement('li');
                bookLi.textContent = bookName;
                const chapterUl = document.createElement('ul');
                for (const chapterNum in scriptureData[divName][bookName]) {
                    const chapterLi = document.createElement('li');
                    chapterLi.className = 'nav-item';
                    chapterLi.textContent = `Chapter ${chapterNum}`;
                    chapterLi.dataset.division = divName;
                    chapterLi.dataset.book = bookName;
                    chapterLi.dataset.chapter = chapterNum;
                    chapterLi.addEventListener('click', handleNavClick);
                    chapterUl.appendChild(chapterLi);
                }
                bookLi.appendChild(chapterUl);
                bookUl.appendChild(bookLi);
            }
            divLi.appendChild(bookUl);
            ul.appendChild(divLi);
        }
        navigationTree.appendChild(ul);
    }

    function handleNavClick(event) {
        const { division, book, chapter } = event.target.dataset;
        displayChapter(division, book, chapter);

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        event.target.classList.add('active');
    }

    // --- Content Display ---
    function displayChapter(division, book, chapter) {
        const verses = scriptureData[division]?.[book]?.[chapter];
        if (!verses) return;

        chapterTitle.textContent = `${book.replace(/\(.*?\)/g, '').trim()} - Chapter ${chapter}`;
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

    // --- Search ---
    function handleSearch() {
        const query = searchInput.value.toLowerCase();
        searchResults.innerHTML = '';

        if (query.length < 2) {
            return;
        }

        const results = flatData.filter(item => item.text.toLowerCase().includes(query));

        results.slice(0, 100).forEach(result => {
            const div = document.createElement('div');
            div.className = 'search-result-item';
            div.addEventListener('click', () => {
                displayChapter(result.division, result.book, result.chapter);
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
            location.textContent = `${result.book.replace(/\(.*?\)/g, '').trim()} ${result.chapter}:${result.verse}`;

            const snippet = document.createElement('div');
            snippet.className = 'text-snippet';
            const highlightedText = result.text.replace(new RegExp(query, 'gi'), (match) => `<strong>${match}</strong>`);
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
