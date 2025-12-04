const API_BASE_URL = '/api';
let currentUser = null;
let token = localStorage.getItem('token');

const authSection = document.getElementById('authSection');
const loginForm = document.getElementById('loginForm');
const userInfo = document.getElementById('userInfo');
const currentUserSpan = document.getElementById('currentUser');
const navbar = document.getElementById('navbar');
const apiStatus = document.getElementById('apiStatus');

let productTypes = [];
let batches = [];
let inspections = [];

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    checkApiStatus();
    
    // Показать дашборд по умолчанию
    showSection('dashboard');
});

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            apiStatus.innerHTML = 'API: <span class="status-online">Подключен</span>';
        } else {
            apiStatus.innerHTML = 'API: <span class="status-offline">Ошибка</span>';
        }
    } catch (error) {
        apiStatus.innerHTML = 'API: <span class="status-offline">Не подключен</span>';
    }
}

function checkAuth() {
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            currentUser = {
                username: payload.sub,
                userId: payload.user_id,
                role: payload.role
            };
            
            updateUIForLoggedInUser();
            loadInitialData();
        } catch (error) {
            console.error('Ошибка декодирования токена:', error);
            logout();
        }
    } else {
        updateUIForLoggedOutUser();
    }
}

function updateUIForLoggedInUser() {
    loginForm.style.display = 'none';
    userInfo.style.display = 'flex';
    navbar.style.display = 'flex';
    
    currentUserSpan.textContent = currentUser.username;
    
    if (currentUser.role === 'admin') {
        document.getElementById('adminSection').style.display = 'block';
        document.getElementById('rolesSection').style.display = 'block';
    }
}

function updateUIForLoggedOutUser() {
    loginForm.style.display = 'block';
    userInfo.style.display = 'none';
    navbar.style.display = 'none';
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        alert('Пожалуйста, введите логин и пароль');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            
            checkAuth();
            
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        } else {
            alert('Неверный логин или пароль');
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        alert('Ошибка подключения к серверу');
    }
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    checkAuth();
    
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById('dashboard').style.display = 'block';
}

async function loadInitialData() {
    if (!token) return;
    
    try {
        const productTypesResponse = await fetchWithAuth(`${API_BASE_URL}/product-types?limit=100`);
        if (productTypesResponse.ok) {
            productTypes = await productTypesResponse.json();
        }
        
        await loadBatches();
        
        await loadInspections();
        
        updateDashboard();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
    }
}

async function fetchWithAuth(url, options = {}) {
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    return fetch(url, {
        ...options,
        headers
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    document.querySelectorAll('.navbar button').forEach(button => {
        button.classList.remove('active');
    });
    
    document.getElementById(sectionId).style.display = 'block';
    
    event.target.classList.add('active');
    
    switch(sectionId) {
        case 'batches':
            loadBatches();
            break;
        case 'inspections':
            loadInspections();
            break;
        case 'dashboard':
            updateDashboard();
            break;
    }
}

async function loadBatches() {
    if (!token) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/batches?limit=100`);
        if (response.ok) {
            batches = await response.json();
            renderBatchesTable();
        }
    } catch (error) {
        console.error('Ошибка загрузки партий:', error);
    }
}

function renderBatchesTable() {
    const tableBody = document.getElementById('batchesTableBody');
    tableBody.innerHTML = '';
    
    batches.forEach(batch => {
        const row = document.createElement('tr');
        
        let statusClass = '';
        switch(batch.status) {
            case 'в производстве': statusClass = 'status-in-production'; break;
            case 'произведено': statusClass = 'status-produced'; break;
            case 'отгружено': statusClass = 'status-shipped'; break;
        }
        
        let qualityStars = '';
        if (batch.quality_rating) {
            for (let i = 0; i < 5; i++) {
                qualityStars += i < batch.quality_rating ? '★' : '☆';
            }
        }
        
        row.innerHTML = `
            <td>${batch.batch_number}</td>
            <td>${batch.product_type ? batch.product_type.type_name : 'Не указан'}</td>
            <td>${new Date(batch.production_date).toLocaleDateString('ru-RU')}</td>
            <td><span class="${statusClass}">${batch.status}</span></td>
            <td>${qualityStars}</td>
            <td>
                <button class="btn-action btn-view" onclick="viewBatch(${batch.id})" title="Просмотр">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-action btn-edit" onclick="editBatch(${batch.id})" title="Редактировать">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-action btn-delete" onclick="deleteBatch(${batch.id})" title="Удалить">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

function searchBatches() {
    const searchTerm = document.getElementById('batchSearch').value.toLowerCase();
    const filteredBatches = batches.filter(batch => 
        batch.batch_number.toLowerCase().includes(searchTerm)
    );
    
    const tableBody = document.getElementById('batchesTableBody');
    tableBody.innerHTML = '';
    
    filteredBatches.forEach(batch => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${batch.batch_number}</td>
            <td>${batch.product_type ? batch.product_type.type_name : 'Не указан'}</td>
            <td>${new Date(batch.production_date).toLocaleDateString('ru-RU')}</td>
            <td>${batch.status}</td>
            <td>${batch.quality_rating || ''}</td>
            <td>
                <button class="btn-action btn-edit" onclick="editBatch(${batch.id})">Изменить</button>
                <button class="btn-action btn-delete" onclick="deleteBatch(${batch.id})">Удалить</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function filterBatches() {
    const status = document.getElementById('batchStatusFilter').value;
    const filteredBatches = status ? 
        batches.filter(batch => batch.status === status) : 
        batches;
    
    const tableBody = document.getElementById('batchesTableBody');
    tableBody.innerHTML = '';
    
    filteredBatches.forEach(batch => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${batch.batch_number}</td>
            <td>${batch.product_type ? batch.product_type.type_name : 'Не указан'}</td>
            <td>${new Date(batch.production_date).toLocaleDateString('ru-RU')}</td>
            <td>${batch.status}</td>
            <td>${batch.quality_rating || ''}</td>
            <td>
                <button class="btn-action btn-edit" onclick="editBatch(${batch.id})">Изменить</button>
                <button class="btn-action btn-delete" onclick="deleteBatch(${batch.id})">Удалить</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function openBatchModal(batchId = null) {
    const modal = document.getElementById('batchModal');
    const modalTitle = document.getElementById('modalTitle');
    
    if (batchId) {
        modalTitle.textContent = 'Редактировать партию';
        const batch = batches.find(b => b.id === batchId);
        
        document.getElementById('batchId').value = batch.id;
        document.getElementById('batchNumber').value = batch.batch_number;
        document.getElementById('productTypeId').value = batch.product_type_id;
        document.getElementById('productionDate').value = batch.production_date;
        document.getElementById('furnaceNumber').value = batch.furnace_number || '';
        document.getElementById('totalWeight').value = batch.total_weight_kg || '';
        document.getElementById('totalLength').value = batch.total_length_m || '';
        document.getElementById('status').value = batch.status;
    } else {
        modalTitle.textContent = 'Добавить партию';
        document.getElementById('batchForm').reset();
        document.getElementById('batchId').value = '';
    }
    
    const productTypeSelect = document.getElementById('productTypeId');
    productTypeSelect.innerHTML = '<option value="">Выберите тип продукции</option>';
    productTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = `${type.type_code} - ${type.type_name}`;
        productTypeSelect.appendChild(option);
    });
    
    document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
}

async function saveBatch() {
    const batchId = document.getElementById('batchId').value;
    const batchData = {
        batch_number: document.getElementById('batchNumber').value,
        product_type_id: parseInt(document.getElementById('productTypeId').value),
        production_date: document.getElementById('productionDate').value,
        furnace_number: document.getElementById('furnaceNumber').value || null,
        total_weight_kg: document.getElementById('totalWeight').value ? parseFloat(document.getElementById('totalWeight').value) : null,
        total_length_m: document.getElementById('totalLength').value ? parseFloat(document.getElementById('totalLength').value) : null,
        status: document.getElementById('status').value
    };
    
    if (!batchData.batch_number || !batchData.product_type_id || !batchData.production_date) {
        alert('Пожалуйста, заполните обязательные поля (отмечены *)');
        return;
    }
    
    try {
        let response;
        
        if (batchId) {
            response = await fetchWithAuth(`${API_BASE_URL}/batches/${batchId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(batchData)
            });
        } else {
            response = await fetchWithAuth(`${API_BASE_URL}/batches`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(batchData)
            });
        }
        
        if (response.ok) {
            closeModal();
            await loadBatches();
            alert(batchId ? 'Партия обновлена' : 'Партия создана');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        console.error('Ошибка сохранения партии:', error);
        alert('Ошибка подключения к серверу');
    }
}

function editBatch(batchId) {
    openBatchModal(batchId);
}

function viewBatch(batchId) {
    const batch = batches.find(b => b.id === batchId);
    if (batch) {
        alert(`
            Детали партии:
            Номер: ${batch.batch_number}
            Тип продукции: ${batch.product_type ? batch.product_type.type_name : 'Не указан'}
            Дата производства: ${new Date(batch.production_date).toLocaleDateString('ru-RU')}
            Статус: ${batch.status}
            Печь: ${batch.furnace_number || 'Не указана'}
            Вес: ${batch.total_weight_kg ? batch.total_weight_kg + ' кг' : 'Не указан'}
            Длина: ${batch.total_length_m ? batch.total_length_m + ' м' : 'Не указана'}
        `);
    }
}

function deleteBatch(batchId) {
    const batch = batches.find(b => b.id === batchId);
    if (batch && confirm(`Вы уверены, что хотите удалить партию "${batch.batch_number}"?`)) {
        fetchWithAuth(`${API_BASE_URL}/batches/${batchId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                loadBatches();
                alert('Партия удалена');
            } else {
                alert('Ошибка при удалении партии');
            }
        })
        .catch(error => {
            console.error('Ошибка удаления партии:', error);
            alert('Ошибка подключения к серверу');
        });
    }
}

async function loadInspections() {
    if (!token) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/inspections?limit=100`);
        if (response.ok) {
            inspections = await response.json();
            renderInspectionsTable();
        }
    } catch (error) {
        console.error('Ошибка загрузки результатов контроля:', error);
    }
}

function renderInspectionsTable() {
    const tableBody = document.getElementById('inspectionsTableBody');
    tableBody.innerHTML = '';
    
    inspections.forEach(inspection => {
        const row = document.createElement('tr');
        
        let verdictClass = '';
        switch(inspection.overall_verdict) {
            case 'соответствует': verdictClass = 'verdict-pass'; break;
            case 'условно соответствует': verdictClass = 'verdict-warning'; break;
            case 'не соответствует': verdictClass = 'verdict-fail'; break;
        }
        
        let statusClass = '';
        switch(inspection.status) {
            case 'обработка': statusClass = 'status-processing'; break;
            case 'проверено': statusClass = 'status-checked'; break;
            case 'утверждено': statusClass = 'status-approved'; break;
        }
        
        row.innerHTML = `
            <td>${inspection.id}</td>
            <td>${inspection.batch ? inspection.batch.batch_number : 'Не указана'}</td>
            <td>${new Date(inspection.inspection_time).toLocaleString('ru-RU')}</td>
            <td><span class="${verdictClass}">${inspection.overall_verdict}</span></td>
            <td><span class="${statusClass}">${inspection.status}</span></td>
            <td>${inspection.defect_count} дефект(ов)</td>
            <td>
                <button class="btn-action btn-view" onclick="viewInspection(${inspection.id})" title="Просмотр">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-action btn-edit" onclick="editInspection(${inspection.id})" title="Редактировать">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-action btn-delete" onclick="deleteInspection(${inspection.id})" title="Удалить">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

function updateDashboard() {
    document.getElementById('totalBatches').textContent = batches.length;
    
    const today = new Date().toISOString().split('T')[0];
    const inspectionsToday = inspections.filter(inspection => 
        inspection.inspection_time.startsWith(today)
    ).length;
    document.getElementById('inspectionsToday').textContent = inspectionsToday;
    
    const totalDefects = inspections.reduce((sum, inspection) => sum + inspection.defect_count, 0);
    document.getElementById('defectsFound').textContent = totalDefects;
    
    const defectPercentage = inspections.length > 0 ? 
        (inspections.filter(i => i.is_defect_detected).length / inspections.length * 100).toFixed(1) : 
        0;
    document.getElementById('defectPercentage').textContent = `${defectPercentage}%`;
    
    const recentInspections = inspections
        .sort((a, b) => new Date(b.inspection_time) - new Date(a.inspection_time))
        .slice(0, 5);
    
    const recentInspectionsDiv = document.getElementById('recentInspections');
    recentInspectionsDiv.innerHTML = '';
    
    recentInspections.forEach(inspection => {
        const div = document.createElement('div');
        div.className = 'recent-inspection-item';
        div.innerHTML = `
            <strong>Партия ${inspection.batch ? inspection.batch.batch_number : 'Не указана'}</strong>
            <span>${new Date(inspection.inspection_time).toLocaleString('ru-RU')}</span>
            <span class="${inspection.is_defect_detected ? 'verdict-fail' : 'verdict-pass'}">
                ${inspection.is_defect_detected ? 'Дефекты найдены' : 'Без дефектов'}
            </span>
        `;
        recentInspectionsDiv.appendChild(div);
    });
}

const style = document.createElement('style');
style.textContent = `
    .status-in-production { color: #2196F3; font-weight: bold; }
    .status-produced { color: #4CAF50; font-weight: bold; }
    .status-shipped { color: #9C27B0; font-weight: bold; }
    
    .status-processing { color: #FF9800; font-weight: bold; }
    .status-checked { color: #2196F3; font-weight: bold; }
    .status-approved { color: #4CAF50; font-weight: bold; }
    
    .verdict-pass { color: #4CAF50; font-weight: bold; }
    .verdict-warning { color: #FF9800; font-weight: bold; }
    .verdict-fail { color: #F44336; font-weight: bold; }
    
    .recent-inspection-item {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
    }
    
    .recent-inspection-item:hover {
        background-color: #f9f9f9;
    }
`;
document.head.appendChild(style);