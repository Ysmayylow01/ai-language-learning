// Admin Panel JavaScript
// Backend API integration we CRUD operations

const API_BASE_URL = 'http://localhost:5000';
let currentData = {
    languages: [],
    lessons: [],
    exercises: [],
    users: [],
    vocabulary: []
};
let editingItem = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadAllData();
    updateExerciseFields(); // Initialize exercise form
});

// Navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
        });
    });
}

function navigateTo(page) {
    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'languages': 'Diller',
        'lessons': 'Sapaklar',
        'exercises': 'Maşklar',
        'users': 'Ulanyjylar',
        'vocabulary': 'Sözlük'
    };
    document.querySelector('.page-title').textContent = titles[page];
    
    // Show page
    document.querySelectorAll('.page-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${page}-page`).classList.add('active');
}

// Load All Data
async function loadAllData() {
    try {
        await Promise.all([
            loadLanguages(),
            loadLessons(),
            loadExercises(),
            loadUsers(),
            loadVocabulary()
        ]);
        updateDashboard();
    } catch (error) {
        showToast('Maglumat ýüklenende ýalňyşlyk!', 'error');
    }
}

// Dashboard
function updateDashboard() {
    document.getElementById('stat-languages').textContent = currentData.languages.length;
    document.getElementById('stat-lessons').textContent = currentData.lessons.length;
    document.getElementById('stat-exercises').textContent = currentData.exercises.length;
    document.getElementById('stat-users').textContent = currentData.users.length;
}

// ===== LANGUAGES =====

async function loadLanguages() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/languages`);
        currentData.languages = await response.json();
        renderLanguagesTable();
        populateLanguageSelects();
    } catch (error) {
        console.error('Languages load error:', error);
    }
}

function renderLanguagesTable() {
    const tbody = document.getElementById('languages-table-body');
    tbody.innerHTML = currentData.languages.map(lang => `
        <tr>
            <td>${lang.id}</td>
            <td style="font-size: 24px;">${lang.flag}</td>
            <td><strong>${lang.name}</strong></td>
            <td><code>${lang.code}</code></td>
            <td>${lang.description || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-secondary" onclick="editLanguage(${lang.id})">
                        ✏️ Üýtget
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteLanguage(${lang.id})">
                        🗑️ Poz
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function showAddLanguageModal() {
    editingItem = null;
    document.getElementById('language-modal-title').textContent = 'Täze dil goş';
    document.getElementById('language-name').value = '';
    document.getElementById('language-code').value = '';
    document.getElementById('language-flag').value = '';
    document.getElementById('language-description').value = '';
    openModal('language-modal');
}

function editLanguage(id) {
    const language = currentData.languages.find(l => l.id === id);
    if (!language) return;
    
    editingItem = language;
    document.getElementById('language-modal-title').textContent = 'Dili üýtget';
    document.getElementById('language-name').value = language.name;
    document.getElementById('language-code').value = language.code;
    document.getElementById('language-flag').value = language.flag;
    document.getElementById('language-description').value = language.description || '';
    openModal('language-modal');
}

async function saveLanguage() {
    const data = {
        name: document.getElementById('language-name').value,
        code: document.getElementById('language-code').value,
        flag: document.getElementById('language-flag').value,
        description: document.getElementById('language-description').value
    };
    
    if (!data.name || !data.code) {
        showToast('Ähli meýdanlary dolduryň!', 'error');
        return;
    }
    
    if (editingItem) {
        // Update existing
        const index = currentData.languages.findIndex(l => l.id === editingItem.id);
        currentData.languages[index] = { ...editingItem, ...data };
        showToast('Dil üýtgedildi!', 'success');
    } else {
        // Add new
        const newId = Math.max(...currentData.languages.map(l => l.id), 0) + 1;
        currentData.languages.push({ id: newId, ...data });
        showToast('Täze dil goşuldy!', 'success');
    }
    
    renderLanguagesTable();
    populateLanguageSelects();
    closeModal('language-modal');
    updateDashboard();
}

async function deleteLanguage(id) {
    if (!confirm('Bu dili pozmak isleýärsiňizmi?')) return;
    
    currentData.languages = currentData.languages.filter(l => l.id !== id);
    renderLanguagesTable();
    showToast('Dil pozuldy!', 'success');
    updateDashboard();
}

function populateLanguageSelects() {
    const lessonSelect = document.getElementById('lesson-language');
    const filterSelect = document.getElementById('lesson-language-filter');
    
    const options = currentData.languages.map(lang => 
        `<option value="${lang.id}">${lang.flag} ${lang.name}</option>`
    ).join('');
    
    if (lessonSelect) lessonSelect.innerHTML = options;
    if (filterSelect) filterSelect.innerHTML = '<option value="">Ähli diller</option>' + options;
}

// ===== LESSONS =====

async function loadLessons() {
    // In production, load from backend for each language
    // For now, we'll display static data structure
    currentData.lessons = [
        { id: 1, language_id: 1, title: 'Salamlaşma', level: 'beginner', order: 1, description: 'Esasy salamlaşma' },
        { id: 2, language_id: 1, title: 'Sanlar', level: 'beginner', order: 2, description: 'Sanlar 0-20' },
    ];
    renderLessonsTable();
    populateLessonSelects();
}

function renderLessonsTable() {
    const tbody = document.getElementById('lessons-table-body');
    tbody.innerHTML = currentData.lessons.map(lesson => {
        const language = currentData.languages.find(l => l.id === lesson.language_id);
        const exerciseCount = currentData.exercises.filter(e => e.lesson_id === lesson.id).length;
        
        return `
            <tr>
                <td>${lesson.id}</td>
                <td><strong>${lesson.title}</strong></td>
                <td>${language ? language.flag + ' ' + language.name : '-'}</td>
                <td><span class="badge badge-${lesson.level}">${lesson.level}</span></td>
                <td>${lesson.order}</td>
                <td>${exerciseCount}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="editLesson(${lesson.id})">
                            ✏️ Üýtget
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteLesson(${lesson.id})">
                            🗑️ Poz
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function filterLessons() {
    const languageId = parseInt(document.getElementById('lesson-language-filter').value);
    const level = document.getElementById('lesson-level-filter').value;
    
    let filtered = currentData.lessons;
    if (languageId) filtered = filtered.filter(l => l.language_id === languageId);
    if (level) filtered = filtered.filter(l => l.level === level);
    
    // Re-render with filtered data
    const tbody = document.getElementById('lessons-table-body');
    tbody.innerHTML = filtered.map(lesson => {
        const language = currentData.languages.find(l => l.id === lesson.language_id);
        const exerciseCount = currentData.exercises.filter(e => e.lesson_id === lesson.id).length;
        
        return `
            <tr>
                <td>${lesson.id}</td>
                <td><strong>${lesson.title}</strong></td>
                <td>${language ? language.flag + ' ' + language.name : '-'}</td>
                <td><span class="badge badge-${lesson.level}">${lesson.level}</span></td>
                <td>${lesson.order}</td>
                <td>${exerciseCount}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="editLesson(${lesson.id})">✏️</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteLesson(${lesson.id})">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function showAddLessonModal() {
    editingItem = null;
    document.getElementById('lesson-modal-title').textContent = 'Täze sapak goş';
    document.getElementById('lesson-title').value = '';
    document.getElementById('lesson-language').value = currentData.languages[0]?.id || '';
    document.getElementById('lesson-level').value = 'beginner';
    document.getElementById('lesson-order').value = currentData.lessons.length + 1;
    document.getElementById('lesson-description').value = '';
    document.getElementById('lesson-content').value = JSON.stringify({
        sections: [
            {
                type: "text",
                content: "Sapak mazmuny"
            },
            {
                type: "vocabulary",
                words: []
            }
        ]
    }, null, 2);
    openModal('lesson-modal');
}

function editLesson(id) {
    const lesson = currentData.lessons.find(l => l.id === id);
    if (!lesson) return;
    
    editingItem = lesson;
    document.getElementById('lesson-modal-title').textContent = 'Sapak üýtget';
    document.getElementById('lesson-title').value = lesson.title;
    document.getElementById('lesson-language').value = lesson.language_id;
    document.getElementById('lesson-level').value = lesson.level;
    document.getElementById('lesson-order').value = lesson.order;
    document.getElementById('lesson-description').value = lesson.description || '';
    document.getElementById('lesson-content').value = JSON.stringify(lesson.content || {sections: []}, null, 2);
    openModal('lesson-modal');
}

function saveLesson() {
    const data = {
        title: document.getElementById('lesson-title').value,
        language_id: parseInt(document.getElementById('lesson-language').value),
        level: document.getElementById('lesson-level').value,
        order: parseInt(document.getElementById('lesson-order').value),
        description: document.getElementById('lesson-description').value
    };
    
    try {
        data.content = JSON.parse(document.getElementById('lesson-content').value);
    } catch (e) {
        showToast('JSON format ýalňyş!', 'error');
        return;
    }
    
    if (!data.title) {
        showToast('Sapagyň adyny ýazyň!', 'error');
        return;
    }
    
    if (editingItem) {
        const index = currentData.lessons.findIndex(l => l.id === editingItem.id);
        currentData.lessons[index] = { ...editingItem, ...data };
        showToast('Sapak üýtgedildi!', 'success');
    } else {
        const newId = Math.max(...currentData.lessons.map(l => l.id), 0) + 1;
        currentData.lessons.push({ id: newId, ...data });
        showToast('Täze sapak goşuldy!', 'success');
    }
    
    renderLessonsTable();
    populateLessonSelects();
    closeModal('lesson-modal');
    updateDashboard();
}

function deleteLesson(id) {
    if (!confirm('Bu sapak we onuň ähli maşklary pozular!')) return;
    
    currentData.lessons = currentData.lessons.filter(l => l.id !== id);
    currentData.exercises = currentData.exercises.filter(e => e.lesson_id !== id);
    renderLessonsTable();
    renderExercisesTable();
    showToast('Sapak pozuldy!', 'success');
    updateDashboard();
}

function populateLessonSelects() {
    const exerciseSelect = document.getElementById('exercise-lesson');
    const filterSelect = document.getElementById('exercise-lesson-filter');
    
    const options = currentData.lessons.map(lesson => {
        const lang = currentData.languages.find(l => l.id === lesson.language_id);
        return `<option value="${lesson.id}">${lang ? lang.flag + ' ' : ''}${lesson.title}</option>`;
    }).join('');
    
    if (exerciseSelect) exerciseSelect.innerHTML = options;
    if (filterSelect) filterSelect.innerHTML = '<option value="">Ähli sapaklar</option>' + options;
}

// ===== EXERCISES =====

async function loadExercises() {
    currentData.exercises = [
        { 
            id: 1, 
            lesson_id: 1, 
            title: 'Hola näme diýmek?', 
            type: 'multiple_choice',
            difficulty: 1,
            points: 10,
            content: {
                question: '"Hola" näme diýmek?',
                options: ['Salam', 'Hoş gal', 'Sag bol'],
                correct_answer: 'Salam',
                hint: 'Bu salamlaşma sözi'
            }
        }
    ];
    renderExercisesTable();
}

function renderExercisesTable() {
    const tbody = document.getElementById('exercises-table-body');
    tbody.innerHTML = currentData.exercises.map(exercise => {
        const lesson = currentData.lessons.find(l => l.id === exercise.lesson_id);
        const typeNames = {
            'multiple_choice': 'Multiple Choice',
            'translation': 'Translation',
            'fill_blank': 'Fill Blank'
        };
        
        return `
            <tr>
                <td>${exercise.id}</td>
                <td><strong>${exercise.title}</strong></td>
                <td>${lesson ? lesson.title : '-'}</td>
                <td><span class="badge">${typeNames[exercise.type]}</span></td>
                <td>${'⭐'.repeat(exercise.difficulty)}</td>
                <td><strong>${exercise.points}</strong></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="editExercise(${exercise.id})">
                            ✏️ Üýtget
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteExercise(${exercise.id})">
                            🗑️ Poz
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function filterExercises() {
    const lessonId = parseInt(document.getElementById('exercise-lesson-filter').value);
    const type = document.getElementById('exercise-type-filter').value;
    
    let filtered = currentData.exercises;
    if (lessonId) filtered = filtered.filter(e => e.lesson_id === lessonId);
    if (type) filtered = filtered.filter(e => e.type === type);
    
    // Re-render
    const tbody = document.getElementById('exercises-table-body');
    tbody.innerHTML = filtered.map(exercise => {
        const lesson = currentData.lessons.find(l => l.id === exercise.lesson_id);
        const typeNames = {
            'multiple_choice': 'Multiple Choice',
            'translation': 'Translation',
            'fill_blank': 'Fill Blank'
        };
        
        return `
            <tr>
                <td>${exercise.id}</td>
                <td><strong>${exercise.title}</strong></td>
                <td>${lesson ? lesson.title : '-'}</td>
                <td><span class="badge">${typeNames[exercise.type]}</span></td>
                <td>${'⭐'.repeat(exercise.difficulty)}</td>
                <td><strong>${exercise.points}</strong></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="editExercise(${exercise.id})">✏️</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteExercise(${exercise.id})">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function showAddExerciseModal() {
    editingItem = null;
    document.getElementById('exercise-modal-title').textContent = 'Täze maşk goş';
    document.getElementById('exercise-lesson').value = currentData.lessons[0]?.id || '';
    document.getElementById('exercise-type').value = 'multiple_choice';
    document.getElementById('exercise-title').value = '';
    document.getElementById('exercise-difficulty').value = '1';
    document.getElementById('exercise-points').value = '10';
    document.getElementById('exercise-question').value = '';
    document.getElementById('exercise-options').value = '';
    document.getElementById('exercise-answer').value = '';
    document.getElementById('exercise-hint').value = '';
    updateExerciseFields();
    openModal('exercise-modal');
}

function editExercise(id) {
    const exercise = currentData.exercises.find(e => e.id === id);
    if (!exercise) return;
    
    editingItem = exercise;
    document.getElementById('exercise-modal-title').textContent = 'Maşk üýtget';
    document.getElementById('exercise-lesson').value = exercise.lesson_id;
    document.getElementById('exercise-type').value = exercise.type;
    document.getElementById('exercise-title').value = exercise.title;
    document.getElementById('exercise-difficulty').value = exercise.difficulty;
    document.getElementById('exercise-points').value = exercise.points;
    document.getElementById('exercise-question').value = exercise.content.question;
    
    if (exercise.content.options) {
        document.getElementById('exercise-options').value = exercise.content.options.join('\n');
    }
    
    document.getElementById('exercise-answer').value = exercise.content.correct_answer;
    document.getElementById('exercise-hint').value = exercise.content.hint || '';
    
    updateExerciseFields();
    openModal('exercise-modal');
}

function updateExerciseFields() {
    const type = document.getElementById('exercise-type').value;
    const optionsGroup = document.getElementById('exercise-options-group');
    
    if (type === 'multiple_choice') {
        optionsGroup.style.display = 'block';
    } else {
        optionsGroup.style.display = 'none';
    }
}

function saveExercise() {
    const type = document.getElementById('exercise-type').value;
    
    const data = {
        lesson_id: parseInt(document.getElementById('exercise-lesson').value),
        title: document.getElementById('exercise-title').value,
        type: type,
        difficulty: parseInt(document.getElementById('exercise-difficulty').value),
        points: parseInt(document.getElementById('exercise-points').value),
        content: {
            question: document.getElementById('exercise-question').value,
            correct_answer: document.getElementById('exercise-answer').value,
            hint: document.getElementById('exercise-hint').value
        }
    };
    
    if (type === 'multiple_choice') {
        const optionsText = document.getElementById('exercise-options').value;
        data.content.options = optionsText.split('\n').filter(o => o.trim());
    }
    
    if (!data.title || !data.content.question) {
        showToast('Ähli meýdanlary dolduryň!', 'error');
        return;
    }
    
    if (editingItem) {
        const index = currentData.exercises.findIndex(e => e.id === editingItem.id);
        currentData.exercises[index] = { ...editingItem, ...data };
        showToast('Maşk üýtgedildi!', 'success');
    } else {
        const newId = Math.max(...currentData.exercises.map(e => e.id), 0) + 1;
        currentData.exercises.push({ id: newId, ...data });
        showToast('Täze maşk goşuldy!', 'success');
    }
    
    renderExercisesTable();
    renderLessonsTable(); // Update exercise counts
    closeModal('exercise-modal');
    updateDashboard();
}

function deleteExercise(id) {
    if (!confirm('Bu maşk pozular!')) return;
    
    currentData.exercises = currentData.exercises.filter(e => e.id !== id);
    renderExercisesTable();
    renderLessonsTable();
    showToast('Maşk pozuldy!', 'success');
    updateDashboard();
}

// ===== USERS =====

async function loadUsers() {
    // Load from backend in production
    currentData.users = [];
    renderUsersTable();
}

function renderUsersTable() {
    const tbody = document.getElementById('users-table-body');
    
    if (currentData.users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Heniz ulanyjy ýok</td></tr>';
        return;
    }
    
    tbody.innerHTML = currentData.users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.email}</td>
            <td>${user.native_language}</td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                    🗑️ Poz
                </button>
            </td>
        </tr>
    `).join('');
}

// ===== VOCABULARY =====

async function loadVocabulary() {
    currentData.vocabulary = [];
    renderVocabularyTable();
}

function renderVocabularyTable() {
    const tbody = document.getElementById('vocabulary-table-body');
    
    if (currentData.vocabulary.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Heniz söz ýok</td></tr>';
        return;
    }
    
    tbody.innerHTML = currentData.vocabulary.map(word => {
        const language = currentData.languages.find(l => l.id === word.language_id);
        return `
            <tr>
                <td>${word.id}</td>
                <td><strong>${word.word}</strong></td>
                <td>${word.translation}</td>
                <td>${language ? language.flag : ''}</td>
                <td>${word.user_id}</td>
                <td>${'⭐'.repeat(word.mastery_level)}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteVocabulary(${word.id})">
                        🗑️ Poz
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// ===== MODAL FUNCTIONS =====

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// ===== TOAST =====

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Export data (for saving to backend)
function exportData() {
    const data = {
        languages: currentData.languages,
        lessons: currentData.lessons,
        exercises: currentData.exercises
    };
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'admin-data.json';
    a.click();
    
    showToast('Maglumat export edildi!', 'success');
}
