// ====================================================
//  Admin Panel - Language Learning App
//  admin-script.js
// ====================================================

const API = '';          // same-origin
let allLanguages = [];
let allLessons    = [];
let allExercises  = [];
let editingId     = null;   // currently editing record id

// ──────────────────────────────────────────────
//  BOOTSTRAP
// ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    initNav();
    await loadAll();
    renderDashboard();
});

async function loadAll() {
    await Promise.all([
        fetchLanguages(),
        fetchLessons(),
        fetchExercises(),
    ]);
}

// ──────────────────────────────────────────────
//  NAVIGATION
// ──────────────────────────────────────────────
function initNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            const page = item.dataset.page;
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
            document.getElementById(`${page}-page`).classList.add('active');
            document.querySelector('.page-title').textContent =
                item.querySelector('.nav-text').textContent;

            // Lazy-load page data
            if (page === 'languages')  renderLanguagesTable();
            if (page === 'lessons')    renderLessonsPage();
            if (page === 'exercises')  renderExercisesPage();
            if (page === 'users')      renderUsersPage();
            if (page === 'vocabulary') renderVocabularyPage();
        });
    });
}

// ──────────────────────────────────────────────
//  API HELPERS
// ──────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
    try {
        const res = await fetch(API + url, {
            headers: { 'Content-Type': 'application/json', ...opts.headers },
            ...opts,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
        return data;
    } catch (err) {
        showToast(err.message, 'error');
        throw err;
    }
}

// ──────────────────────────────────────────────
//  FETCH DATA
// ──────────────────────────────────────────────
async function fetchLanguages() {
    allLanguages = await apiFetch('/api/languages');
    populateLanguageSelects();
}

async function fetchLessons() {
    // Fetch lessons for every language
    const results = await Promise.all(
        allLanguages.map(l => apiFetch(`/api/lessons?language_id=${l.id}`).catch(() => []))
    );
    allLessons = results.flat();
    populateLessonSelects();
}

async function fetchExercises() {
    // Fetch exercises for every lesson
    const results = await Promise.all(
        allLessons.map(l =>
            apiFetch(`/api/lessons/${l.id}`)
                .then(d => (d.exercises || []).map(e => ({ ...e, lesson_title: l.title })))
                .catch(() => [])
        )
    );
    allExercises = results.flat();
}

// ──────────────────────────────────────────────
//  POPULATE SELECTS
// ──────────────────────────────────────────────
function populateLanguageSelects() {
    const opts = allLanguages.map(l => `<option value="${l.id}">${l.flag || ''} ${l.name}</option>`).join('');

    // Filter dropdown on Lessons page
    const lf = document.getElementById('lesson-language-filter');
    if (lf) lf.innerHTML = `<option value="">Ähli diller</option>${opts}`;

    // Modal select inside Add Lesson
    const ls = document.getElementById('lesson-language');
    if (ls) ls.innerHTML = opts;
}

function populateLessonSelects() {
    const opts = allLessons.map(l => `<option value="${l.id}">${l.title}</option>`).join('');

    const ef = document.getElementById('exercise-lesson-filter');
    if (ef) ef.innerHTML = `<option value="">Ähli sapaklar</option>${opts}`;

    const es = document.getElementById('exercise-lesson');
    if (es) es.innerHTML = opts;
}

// ──────────────────────────────────────────────
//  DASHBOARD
// ──────────────────────────────────────────────
async function renderDashboard() {
    try {
        const stats = await apiFetch('/api/stats');
        setText('stat-languages',  stats.languages);
        setText('stat-lessons',    stats.lessons);
        setText('stat-exercises',  stats.exercises);
        setText('stat-users',      stats.users);
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  LANGUAGES PAGE
// ──────────────────────────────────────────────
function renderLanguagesTable() {
    const tbody = document.getElementById('languages-table-body');
    if (!tbody) return;

    if (!allLanguages.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Dil ýok</td></tr>`;
        return;
    }

    tbody.innerHTML = allLanguages.map(l => `
        <tr>
            <td><span class="badge">${l.id}</span></td>
            <td class="flag-cell">${l.flag || '—'}</td>
            <td><strong>${escHtml(l.name)}</strong></td>
            <td><code>${escHtml(l.code)}</code></td>
            <td class="desc-cell">${escHtml(l.description || '')}</td>
            <td class="actions-cell">
                <button class="btn-icon edit"   onclick="editLanguage(${l.id})" title="Üýtget">✏️</button>
                <button class="btn-icon delete" onclick="deleteLanguage(${l.id})" title="Öçür">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function showAddLanguageModal() {
    editingId = null;
    clearForm(['language-name','language-code','language-flag','language-description']);
    setText('language-modal-title', 'Täze dil goş');
    openModal('language-modal');
}

function editLanguage(id) {
    const lang = allLanguages.find(l => l.id === id);
    if (!lang) return;
    editingId = id;
    setVal('language-name',        lang.name);
    setVal('language-code',        lang.code);
    setVal('language-flag',        lang.flag || '');
    setVal('language-description', lang.description || '');
    setText('language-modal-title', 'Dili üýtget');
    openModal('language-modal');
}

async function saveLanguage() {
    const body = {
        name:        getVal('language-name').trim(),
        code:        getVal('language-code').trim(),
        flag:        getVal('language-flag').trim(),
        description: getVal('language-description').trim(),
    };
    if (!body.name || !body.code) { showToast('Ady we kody dolduryň', 'error'); return; }

    try {
        if (editingId) {
            await apiFetch(`/api/languages/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
            showToast('Dil üýtgedildi ✅');
        } else {
            await apiFetch('/api/languages', { method: 'POST', body: JSON.stringify(body) });
            showToast('Täze dil goşuldy ✅');
        }
        closeModal('language-modal');
        await fetchLanguages();
        renderLanguagesTable();
        renderDashboard();
    } catch (_) {}
}

async function deleteLanguage(id) {
    if (!confirm('Bu dili öçürmek isleýärsiňizmi?')) return;
    try {
        await apiFetch(`/api/languages/${id}`, { method: 'DELETE' });
        showToast('Dil öçürildi');
        await fetchLanguages();
        await fetchLessons();
        renderLanguagesTable();
        renderDashboard();
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  LESSONS PAGE
// ──────────────────────────────────────────────
function renderLessonsPage() {
    populateLanguageSelects();
    renderLessonsTable(allLessons);
}

async function filterLessons() {
    const langId  = getVal('lesson-language-filter');
    const levelId = getVal('lesson-level-filter');

    let filtered = allLessons;
    if (langId)  filtered = filtered.filter(l => String(l.language_id) === langId);
    if (levelId) filtered = filtered.filter(l => l.level === levelId);
    renderLessonsTable(filtered);
}

function renderLessonsTable(lessons) {
    const tbody = document.getElementById('lessons-table-body');
    if (!tbody) return;

    if (!lessons.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Sapak ýok</td></tr>`;
        return;
    }

    tbody.innerHTML = lessons.map(l => {
        const lang = allLanguages.find(x => x.id === l.language_id);
        return `
        <tr>
            <td><span class="badge">${l.id}</span></td>
            <td><strong>${escHtml(l.title)}</strong></td>
            <td>${lang ? `${lang.flag || ''} ${escHtml(lang.name)}` : l.language_id}</td>
            <td><span class="level-badge ${l.level}">${l.level}</span></td>
            <td>${l.order_num}</td>
            <td><span class="count-badge">${l.exercises_count ?? '—'}</span></td>
            <td class="actions-cell">
                <button class="btn-icon edit"   onclick="editLesson(${l.id})"   title="Üýtget">✏️</button>
                <button class="btn-icon delete" onclick="deleteLesson(${l.id})" title="Öçür">🗑️</button>
            </td>
        </tr>`;
    }).join('');
}

function showAddLessonModal() {
    editingId = null;
    clearForm(['lesson-title','lesson-description','lesson-content','lesson-order']);
    setVal('lesson-order', '1');
    setVal('lesson-content', JSON.stringify({ sections: [] }, null, 2));
    setText('lesson-modal-title', 'Täze sapak goş');
    populateLanguageSelects();
    openModal('lesson-modal');
}

async function editLesson(id) {
    try {
        const lesson = await apiFetch(`/api/lessons/${id}`);
        editingId = id;
        setVal('lesson-title',       lesson.title);
        setVal('lesson-description', lesson.description || '');
        setVal('lesson-level',       lesson.level);
        setVal('lesson-order',       lesson.order_num);
        setVal('lesson-language',    lesson.language_id);
        setVal('lesson-content',     JSON.stringify(lesson.content || {}, null, 2));
        setText('lesson-modal-title', 'Sapak üýtget');
        openModal('lesson-modal');
    } catch (_) {}
}

async function saveLesson() {
    let content;
    try { content = JSON.parse(getVal('lesson-content') || '{}'); }
    catch { showToast('Content JSON formaty ýalňyş', 'error'); return; }

    const body = {
        language_id: parseInt(getVal('lesson-language')),
        title:       getVal('lesson-title').trim(),
        description: getVal('lesson-description').trim(),
        level:       getVal('lesson-level'),
        order_num:   parseInt(getVal('lesson-order')) || 1,
        content,
    };
    if (!body.title) { showToast('Sapa adyny giriziň', 'error'); return; }

    try {
        if (editingId) {
            await apiFetch(`/api/lessons/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
            showToast('Sapak üýtgedildi ✅');
        } else {
            await apiFetch('/api/lessons', { method: 'POST', body: JSON.stringify(body) });
            showToast('Täze sapak goşuldy ✅');
        }
        closeModal('lesson-modal');
        await fetchLessons();
        renderLessonsTable(allLessons);
        renderDashboard();
    } catch (_) {}
}

async function deleteLesson(id) {
    if (!confirm('Bu sapak öçürilsin?')) return;
    try {
        await apiFetch(`/api/lessons/${id}`, { method: 'DELETE' });
        showToast('Sapak öçürildi');
        await fetchLessons();
        renderLessonsTable(allLessons);
        renderDashboard();
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  EXERCISES PAGE
// ──────────────────────────────────────────────
function renderExercisesPage() {
    populateLessonSelects();
    renderExercisesTable(allExercises);
}

function filterExercises() {
    const lessonId = getVal('exercise-lesson-filter');
    const typeId   = getVal('exercise-type-filter');
    let filtered = allExercises;
    if (lessonId) filtered = filtered.filter(e => String(e.lesson_id) === lessonId);
    if (typeId)   filtered = filtered.filter(e => e.type === typeId);
    renderExercisesTable(filtered);
}

function renderExercisesTable(exercises) {
    const tbody = document.getElementById('exercises-table-body');
    if (!tbody) return;

    if (!exercises.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Maşk ýok</td></tr>`;
        return;
    }

    tbody.innerHTML = exercises.map(e => {
        const lesson = allLessons.find(l => l.id === e.lesson_id);
        return `
        <tr>
            <td><span class="badge">${e.id}</span></td>
            <td><strong>${escHtml(e.title)}</strong></td>
            <td>${lesson ? escHtml(lesson.title) : e.lesson_id}</td>
            <td><span class="type-badge ${e.type}">${e.type}</span></td>
            <td>${'⭐'.repeat(e.difficulty || 1)}</td>
            <td><strong>${e.points}</strong></td>
            <td class="actions-cell">
                <button class="btn-icon edit"   onclick="editExercise(${e.id})"   title="Üýtget">✏️</button>
                <button class="btn-icon delete" onclick="deleteExercise(${e.id})" title="Öçür">🗑️</button>
            </td>
        </tr>`;
    }).join('');
}

function showAddExerciseModal() {
    editingId = null;
    clearForm(['exercise-title','exercise-question','exercise-options','exercise-answer','exercise-hint']);
    setVal('exercise-difficulty', '1');
    setVal('exercise-points', '10');
    setVal('exercise-type', 'multiple_choice');
    setText('exercise-modal-title', 'Täze maşk goş');
    updateExerciseFields();
    populateLessonSelects();
    openModal('exercise-modal');
}

async function editExercise(id) {
    try {
        const ex = await apiFetch(`/api/exercises/${id}`);
        editingId = id;
        const c = ex.content || {};
        setVal('exercise-lesson',     ex.lesson_id);
        setVal('exercise-type',       ex.type);
        setVal('exercise-title',      ex.title);
        setVal('exercise-difficulty', ex.difficulty);
        setVal('exercise-points',     ex.points);
        setVal('exercise-question',   c.question || '');
        setVal('exercise-options',    (c.options || []).join('\n'));
        setVal('exercise-answer',     c.correct_answer || '');
        setVal('exercise-hint',       c.hint || '');
        setText('exercise-modal-title', 'Maşk üýtget');
        updateExerciseFields();
        openModal('exercise-modal');
    } catch (_) {}
}

function updateExerciseFields() {
    const type = getVal('exercise-type');
    const group = document.getElementById('exercise-options-group');
    if (group) group.style.display = (type === 'multiple_choice') ? '' : 'none';
}

async function saveExercise() {
    const type    = getVal('exercise-type');
    const options = getVal('exercise-options').split('\n').map(s => s.trim()).filter(Boolean);

    const content = {
        question:       getVal('exercise-question').trim(),
        correct_answer: getVal('exercise-answer').trim(),
        hint:           getVal('exercise-hint').trim(),
    };
    if (type === 'multiple_choice') content.options = options;

    const body = {
        lesson_id:  parseInt(getVal('exercise-lesson')),
        type,
        title:      getVal('exercise-title').trim(),
        difficulty: parseInt(getVal('exercise-difficulty')) || 1,
        points:     parseInt(getVal('exercise-points')) || 10,
        content,
    };
    if (!body.title || !content.question || !content.correct_answer) {
        showToast('Ähli hökmany meýdanlary dolduryň', 'error'); return;
    }

    try {
        if (editingId) {
            await apiFetch(`/api/exercises/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
            showToast('Maşk üýtgedildi ✅');
        } else {
            await apiFetch('/api/exercises', { method: 'POST', body: JSON.stringify(body) });
            showToast('Täze maşk goşuldy ✅');
        }
        closeModal('exercise-modal');
        await fetchExercises();
        renderExercisesTable(allExercises);
        renderDashboard();
    } catch (_) {}
}

async function deleteExercise(id) {
    if (!confirm('Bu maşk öçürilsin?')) return;
    try {
        await apiFetch(`/api/exercises/${id}`, { method: 'DELETE' });
        showToast('Maşk öçürildi');
        await fetchExercises();
        renderExercisesTable(allExercises);
        renderDashboard();
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  USERS PAGE
// ──────────────────────────────────────────────
async function renderUsersPage() {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;

    try {
        const users = await apiFetch('/api/admin/users');
        if (!users.length) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Ulanyjy ýok</td></tr>`;
            return;
        }
        tbody.innerHTML = users.map(u => `
            <tr>
                <td><span class="badge">${u.id}</span></td>
                <td><strong>${escHtml(u.username)}</strong></td>
                <td>${escHtml(u.email)}</td>
                <td>${escHtml(u.native_language || '—')}</td>
                <td class="date-cell">${fmtDate(u.created_at)}</td>
                <td class="actions-cell">
                    <button class="btn-icon delete" onclick="deleteUser(${u.id})" title="Öçür">🗑️</button>
                </td>
            </tr>`).join('');
    } catch (_) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Maglumatlary ýükläp bolmady</td></tr>`;
    }
}

async function deleteUser(id) {
    if (!confirm('Bu ulanyjy öçürilsin?')) return;
    try {
        await apiFetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        showToast('Ulanyjy öçürildi');
        renderUsersPage();
        renderDashboard();
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  VOCABULARY PAGE
// ──────────────────────────────────────────────
async function renderVocabularyPage() {
    const tbody = document.getElementById('vocabulary-table-body');
    if (!tbody) return;

    try {
        const words = await apiFetch('/api/admin/vocabulary');
        if (!words.length) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Söz ýok</td></tr>`;
            return;
        }
        tbody.innerHTML = words.map(w => {
            const lang = allLanguages.find(l => l.id === w.language_id);
            const stars = '⭐'.repeat(w.mastery_level || 0) || '—';
            return `
            <tr>
                <td><span class="badge">${w.id}</span></td>
                <td><strong>${escHtml(w.word)}</strong></td>
                <td>${escHtml(w.translation)}</td>
                <td>${lang ? `${lang.flag || ''} ${escHtml(lang.name)}` : w.language_id}</td>
                <td>${escHtml(w.username || String(w.user_id))}</td>
                <td>${stars}</td>
                <td class="actions-cell">
                    <button class="btn-icon delete" onclick="deleteVocabWord(${w.id})" title="Öçür">🗑️</button>
                </td>
            </tr>`;
        }).join('');
    } catch (_) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Maglumatlary ýükläp bolmady</td></tr>`;
    }
}

async function deleteVocabWord(id) {
    if (!confirm('Bu söz öçürilsin?')) return;
    try {
        await apiFetch(`/api/admin/vocabulary/${id}`, { method: 'DELETE' });
        showToast('Söz öçürildi');
        renderVocabularyPage();
    } catch (_) {}
}

// ──────────────────────────────────────────────
//  MODAL HELPERS
// ──────────────────────────────────────────────
function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); editingId = null; }

// Close on backdrop click
document.addEventListener('click', e => {
    if (e.target.classList.contains('modal')) closeModal(e.target.id);
});

// ──────────────────────────────────────────────
//  TOAST
// ──────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = 'success') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = `toast show ${type}`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 3000);
}

// ──────────────────────────────────────────────
//  TINY UTILS
// ──────────────────────────────────────────────
function getVal(id)         { return (document.getElementById(id)?.value ?? ''); }
function setVal(id, v)      { const el = document.getElementById(id); if (el) el.value = v ?? ''; }
function setText(id, v)     { const el = document.getElementById(id); if (el) el.textContent = v ?? ''; }
function clearForm(ids)     { ids.forEach(id => setVal(id, '')); }
function escHtml(str = '')  { return String(str).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function fmtDate(iso)       { if (!iso) return '—'; try { return new Date(iso).toLocaleDateString('tk-TK'); } catch { return iso; } }