// Funções auxiliares
function showLoading(element) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

function showError(element, message) {
    element.innerHTML = `<div class="error">${message}</div>`;
}

function showSuccess(element, message) {
    element.innerHTML = `<div class="success">${message}</div>`;
}

async function apiCall(url, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Login
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                showError(loginForm, 'Email ou password incorretos');
            }
        } catch (error) {
            showError(loginForm, 'Erro ao fazer login');
        }
    });
}

// Nova Auditoria
const novaAuditoriaForm = document.getElementById('novaAuditoriaForm');
if (novaAuditoriaForm) {
    novaAuditoriaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            empresa: document.getElementById('empresa').value,
            local: document.getElementById('local').value,
            objetivo: document.getElementById('objetivo').value,
            tipo: document.getElementById('tipo').value,
            duracao: document.getElementById('duracao').value,
        };
        
        try {
            const response = await apiCall('/nova-auditoria', 'POST', data);
            window.location.href = `/auditoria/${response.id}/ambito`;
        } catch (error) {
            showError(novaAuditoriaForm, 'Erro ao criar auditoria');
        }
    });
}

// Checklist Split View
const checklistItems = document.querySelectorAll('.checklist-item');
checklistItems.forEach((item, index) => {
    item.addEventListener('click', () => {
        checklistItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        // Carregar detalhes do requisito
    });
});

console.log('App.js carregado com sucesso');
