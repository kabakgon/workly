let allProjects = [];
let currentPage = 1;
let filterMyProjects = false; // Filter for "My Projects"

async function loadProjects() {
    const content = document.getElementById('projects-content');
    
    // Show loading spinner
    content.innerHTML = `
        <div class="flex justify-center items-center h-64">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
    `;
    
    try {
        const status = document.getElementById('filter-status').value;
        const priority = document.getElementById('filter-priority').value;
        const search = document.getElementById('search-input').value;
        
        let url = '/projects/';
        const params = [];
        
        // Add owner filter if "My Projects" is active
        if (filterMyProjects && window.currentUserId) {
            params.push(`owner=${window.currentUserId}`);
        }
        
        if (status) params.push(`status=${status}`);
        if (priority) params.push(`priority=${priority}`);
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        params.push(`page=${currentPage}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        const response = await window.WorklyAPI.request(url);
        allProjects = response.results || response || [];
        
        if (Array.isArray(allProjects)) {
            renderProjects();
        } else {
            throw new Error('Nieprawidłowy format odpowiedzi z API');
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        content.innerHTML = `
            <div class="alert alert-error">
                <span>Błąd podczas ładowania projektów: ${error.message}</span>
                <p class="text-sm mt-2">Sprawdź konsolę przeglądarki (F12) dla szczegółów.</p>
            </div>
        `;
    }
}

function renderProjects() {
    const content = document.getElementById('projects-content');
    
    if (allProjects.length === 0) {
        content.innerHTML = `
            <div class="alert alert-info">
                <span>Brak projektów. Utwórz pierwszy projekt!</span>
            </div>
        `;
        return;
    }
    
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${allProjects.map(project => `
                <div class="card bg-base-200 shadow-lg hover:shadow-xl transition-shadow">
                    <div class="card-body">
                        <h2 class="card-title">
                            <a href="/projects/${project.id}/" class="link link-primary">${project.name}</a>
                        </h2>
                        <p class="text-sm text-base-content/70 line-clamp-2">${project.description || 'Brak opisu'}</p>
                        <div class="flex flex-wrap gap-2 mt-2">
                            ${window.WorklyAPI.getStatusBadge(project.status, 'project')}
                            ${window.WorklyAPI.getPriorityBadge(project.priority)}
                        </div>
                        <div class="text-sm text-base-content/70 mt-2">
                            <p>Zadania: ${project.tasks_count || 0}</p>
                            ${project.start_date ? `<p>Start: ${window.WorklyAPI.formatDate(project.start_date)}</p>` : ''}
                            ${project.end_date ? `<p>Koniec: ${window.WorklyAPI.formatDate(project.end_date)}</p>` : ''}
                        </div>
                        <div class="card-actions justify-end mt-4">
                            <a href="/projects/${project.id}/" class="btn btn-sm btn-primary">Zobacz</a>
                            <button class="btn btn-sm btn-error" onclick="deleteProject(${project.id}, event)" data-project-name="${(project.name || '').replace(/"/g, '&quot;')}">Usuń</button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Wait for WorklyAPI to be available
    if (typeof window.WorklyAPI === 'undefined') {
        // Retry after a short delay
        setTimeout(() => {
            if (typeof window.WorklyAPI !== 'undefined') {
                loadProjects();
            } else {
                console.error('WorklyAPI is not available');
                document.getElementById('projects-content').innerHTML = `
                    <div class="alert alert-error">
                        <span>Błąd: WorklyAPI nie jest dostępne. Odśwież stronę.</span>
                    </div>
                `;
            }
        }, 100);
    } else {
        loadProjects();
    }
    
    document.getElementById('filter-status').addEventListener('change', () => {
        currentPage = 1;
        loadProjects();
    });
    
    document.getElementById('filter-priority').addEventListener('change', () => {
        currentPage = 1;
        loadProjects();
    });
    
    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentPage = 1;
            loadProjects();
        }, 500);
    });
    
    // Setup "My Projects" filter button
    setupFilterButton();
    
    // Load users for owner dropdown
    loadUsersForProjectForm();
    
    // Set default start date to today immediately
    const createModal = document.getElementById('create-project-modal');
    const startDateInput = document.getElementById('start-date');
    
    // Set date immediately when page loads
    if (startDateInput) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.value = today;
    }
    
    function setDefaultStartDate() {
        if (startDateInput) {
            const today = new Date().toISOString().split('T')[0];
            // Always set to today when modal opens
            startDateInput.value = today;
        }
    }
    
    // Set date when modal is opened
    if (createModal) {
        // Listen for dialog open using MutationObserver
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'open') {
                    if (createModal.open) {
                        setDefaultStartDate();
                    }
                }
            });
        });
        observer.observe(createModal, { attributes: true, attributeFilter: ['open'] });
        
        // Also set on click of "Nowy projekt" button
        const newProjectBtn = document.querySelector('[onclick*="create-project-modal"]');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', () => {
                setTimeout(setDefaultStartDate, 50);
                setTimeout(setDefaultOwner, 50);
            });
        }
        
        // Override showModal to set date and owner
        const originalShowModal = createModal.showModal;
        if (originalShowModal) {
            createModal.showModal = function() {
                originalShowModal.call(this);
                setTimeout(setDefaultStartDate, 10);
                setTimeout(setDefaultOwner, 10);
            };
        }
        
        function setDefaultOwner() {
            const ownerSelect = document.getElementById('project-owner');
            if (ownerSelect && window.currentUserId) {
                ownerSelect.value = window.currentUserId;
            }
        }
    }

    // Helper function to show error on control
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            // Remove input-bordered and add input-error
            field.classList.remove('input-bordered');
            field.classList.add('input-error');
            // Set title and aria-label for accessibility
            field.setAttribute('title', message);
            field.setAttribute('aria-label', message);
            field.setAttribute('aria-invalid', 'true');
        }
    }

    // Helper function to clear error
    function clearError(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            // Remove input-error and restore input-bordered
            field.classList.remove('input-error');
            field.classList.add('input-bordered');
            field.removeAttribute('title');
            field.removeAttribute('aria-label');
            field.removeAttribute('aria-invalid');
        }
    }

    // Clear errors on input change
    const endDateInput = document.getElementById('end-date');
    
    if (startDateInput) {
        startDateInput.addEventListener('input', () => {
            clearError('start-date');
        });
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('input', () => {
            clearError('end-date');
        });
    }

    // Create project form
    document.getElementById('create-project-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous errors
        clearError('start-date');
        clearError('end-date');
        
        let hasError = false;
        
        // Validate start date
        const startDate = document.getElementById('start-date').value;
        if (!startDate) {
            showError('start-date', 'Data rozpoczęcia jest wymagana');
            hasError = true;
        }
        
        // Validate end date
        const endDate = document.getElementById('end-date').value;
        if (!endDate) {
            showError('end-date', 'Data zakończenia jest wymagana');
            hasError = true;
        }
        
        if (hasError) {
            return;
        }

        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Convert empty owner to null, otherwise convert to integer
        if (!data.owner) {
            data.owner = null;
        } else {
            data.owner = parseInt(data.owner);
        }
        
        // Convert priority to integer
        data.priority = parseInt(data.priority);
        
        try {
            await window.WorklyAPI.request('/projects/', {
                method: 'POST',
                body: JSON.stringify(data),
            });
            
            document.getElementById('create-project-modal').close();
            e.target.reset();
            // Reset start date to today after form reset
            if (startDateInput) {
                const today = new Date().toISOString().split('T')[0];
                startDateInput.value = today;
            }
            loadProjects();
        } catch (error) {
            alert('Błąd podczas tworzenia projektu: ' + error.message);
        }
    });
});

// Setup filter button
function setupFilterButton() {
    const filterMyProjectsBtn = document.getElementById('filter-my-projects');
    if (filterMyProjectsBtn) {
        // Remove any existing event listeners by cloning the button
        const newBtn = filterMyProjectsBtn.cloneNode(true);
        filterMyProjectsBtn.parentNode.replaceChild(newBtn, filterMyProjectsBtn);
        
        // Set initial state
        if (filterMyProjects) {
            newBtn.classList.add('btn-active');
            newBtn.classList.remove('btn-outline');
        } else {
            newBtn.classList.remove('btn-active');
            newBtn.classList.add('btn-outline');
        }
        
        newBtn.addEventListener('click', () => {
            filterMyProjects = !filterMyProjects;
            if (filterMyProjects) {
                newBtn.classList.add('btn-active');
                newBtn.classList.remove('btn-outline');
            } else {
                newBtn.classList.remove('btn-active');
                newBtn.classList.add('btn-outline');
            }
            currentPage = 1;
            loadProjects();
        });
    }
}

// Load users for project form
async function loadUsersForProjectForm() {
    try {
        const users = await window.WorklyAPI.request('/users/');
        const userList = Array.isArray(users) ? users : [];
        const ownerSelect = document.getElementById('project-owner');
        
        if (ownerSelect) {
            ownerSelect.innerHTML = '<option value="">Brak</option>';
            userList.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                ownerSelect.appendChild(option);
            });
            
            // Set default to current user if available
            if (window.currentUserId) {
                ownerSelect.value = window.currentUserId;
            }
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Delete project function
async function deleteProject(projectId, event) {
    // Get project name from button data attribute
    const button = event ? event.target.closest('button') : null;
    const projectName = button ? button.getAttribute('data-project-name') || 'ten projekt' : 'ten projekt';
    
    window.showConfirmModal(
        `Czy na pewno chcesz usunąć projekt "${projectName}"?`,
        async () => {
            try {
                await window.WorklyAPI.request(`/projects/${projectId}/`, {
                    method: 'DELETE',
                });
                
                // Reload projects
                loadProjects();
            } catch (error) {
                console.error('Error deleting project:', error);
                let errorMessage = 'Błąd podczas usuwania projektu: ' + error.message;
                
                // Check if error is about protected deletion (project has tasks)
                if (error.message && error.message.includes('zadania')) {
                    errorMessage = 'Nie można usunąć projektu, który ma przypięte zadania.';
                }
                
                window.showAlertModal(errorMessage);
            }
        }
    );
}

