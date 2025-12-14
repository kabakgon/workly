let allTasks = [];
let projectsMap = {}; // Cache for project names
let filterMyTasks = false; // Filter for "My Tasks"

async function loadTasks() {
    const content = document.getElementById('tasks-content');
    
    // Show loading spinner
    content.innerHTML = `
        <div class="flex justify-center items-center h-64">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
    `;
    
    try {
        const status = document.getElementById('filter-status').value;
        const search = document.getElementById('search-input').value;
        
        let url = '/tasks/';
        const params = [];
        
        // Add assignee filter if "My Tasks" is active
        if (filterMyTasks && window.currentUserId) {
            params.push(`assignee=${window.currentUserId}`);
        }
        
        if (status) params.push(`status=${status}`);
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        const response = await window.WorklyAPI.request(url);
        allTasks = response.results || response || [];
        
        // Load projects to get names
        await loadProjectsMap();
        
        if (Array.isArray(allTasks)) {
            renderTasks();
        } else {
            throw new Error('Nieprawidłowy format odpowiedzi z API');
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        content.innerHTML = `
            <div class="alert alert-error">
                <span>Błąd podczas ładowania zadań: ${error.message}</span>
                <p class="text-sm mt-2">Sprawdź konsolę przeglądarki (F12) dla szczegółów.</p>
            </div>
        `;
    }
}

// Load projects and create a map for quick lookup
async function loadProjectsMap() {
    try {
        const projects = await window.WorklyAPI.request('/projects/');
        const projectList = projects.results || projects || [];
        projectsMap = {};
        projectList.forEach(project => {
            projectsMap[project.id] = project.name;
        });
    } catch (error) {
        console.error('Error loading projects map:', error);
    }
}

function renderTasks() {
    const content = document.getElementById('tasks-content');
    
    if (allTasks.length === 0) {
        content.innerHTML = `
            <div class="alert alert-info">
                <span>Brak zadań.</span>
            </div>
        `;
        return;
    }
    
    content.innerHTML = `
        <div class="overflow-x-auto">
            <table class="table table-zebra">
                <thead>
                    <tr>
                        <th>Tytuł</th>
                        <th>Projekt</th>
                        <th>Status</th>
                        <th>Postęp</th>
                        <th>Data rozpoczęcia</th>
                        <th>Data zakończenia</th>
                        <th>Akcje</th>
                    </tr>
                </thead>
                <tbody>
                    ${allTasks.map(task => {
                        // Get project name - handle both object and ID
                        let projectName = '-';
                        if (task.project) {
                            if (typeof task.project === 'object') {
                                projectName = task.project.name || '-';
                            } else {
                                // task.project is an ID, look it up in projectsMap
                                projectName = projectsMap[task.project] || task.project || '-';
                            }
                        }
                        return `
                        <tr>
                            <td class="font-semibold">${task.title}</td>
                            <td>${projectName}</td>
                            <td>${window.WorklyAPI.getStatusBadge(task.status, 'task')}</td>
                            <td>
                                <div class="flex items-center gap-2">
                                    <progress class="progress progress-primary w-24" value="${task.progress || 0}" max="100"></progress>
                                    <span class="text-sm">${task.progress || 0}%</span>
                                </div>
                            </td>
                            <td>${window.WorklyAPI.formatDate(task.start_date)}</td>
                            <td>${window.WorklyAPI.formatDate(task.end_date)}</td>
                            <td>
                                <div class="flex gap-2">
                                    <button class="btn btn-sm btn-ghost" onclick="editTask(${task.id})">Edytuj</button>
                                    <button class="btn btn-sm btn-error" onclick="deleteTask(${task.id}, event)" data-task-title="${(task.title || '').replace(/"/g, '&quot;')}">Usuń</button>
                                </div>
                            </td>
                        </tr>
                    `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function editTask(taskId) {
    try {
        // Load task data
        const task = await window.WorklyAPI.request(`/tasks/${taskId}/`);
        
        // Fill edit form
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-task-title').value = task.title || '';
        document.getElementById('edit-task-description').value = task.description || '';
        document.getElementById('edit-task-start-date').value = task.start_date || '';
        document.getElementById('edit-task-end-date').value = task.end_date || '';
        document.getElementById('edit-task-status').value = task.status || 'todo';
        document.getElementById('edit-task-progress').value = task.progress || 0;
        
        // Load projects and set selected project
        await loadProjectsForEditForm();
        const projectId = typeof task.project === 'object' ? task.project.id : task.project;
        document.getElementById('edit-task-project').value = projectId || '';
        
        // Load parent tasks for the project
        if (projectId) {
            await loadParentTasksForEditForm(projectId, task.id);
            const parentId = typeof task.parent === 'object' ? task.parent?.id : task.parent;
            document.getElementById('edit-task-parent').value = parentId || '';
        }
        
        // Load users and set assignee
        await loadUsersForTaskForm();
        if (task.assignee) {
            const assigneeSelect = document.getElementById('edit-task-assignee');
            if (assigneeSelect) {
                // If assignee is an object, use its ID, otherwise use the value directly
                const assigneeId = typeof task.assignee === 'object' ? task.assignee.id : task.assignee;
                assigneeSelect.value = assigneeId || '';
            }
        }
        
        // Open modal
        document.getElementById('edit-task-modal').showModal();
    } catch (error) {
        console.error('Error loading task:', error);
        alert('Błąd podczas ładowania zadania: ' + error.message);
    }
}

// Helper function to show error on control
function showTaskError(fieldId, errorLabelId, message) {
    const field = document.getElementById(fieldId);
    const errorLabel = document.getElementById(errorLabelId);
    if (field && errorLabel) {
        field.classList.remove('input-bordered');
        field.classList.add('input-error');
        errorLabel.classList.remove('hidden');
        errorLabel.querySelector('span').textContent = message;
    }
}

// Helper function to clear error
function clearTaskError(fieldId, errorLabelId) {
    const field = document.getElementById(fieldId);
    const errorLabel = document.getElementById(errorLabelId);
    if (field && errorLabel) {
        field.classList.remove('input-error');
        field.classList.add('input-bordered');
        errorLabel.classList.add('hidden');
    }
}

// Load users for task form
async function loadUsersForTaskForm() {
    try {
        const users = await window.WorklyAPI.request('/users/');
        const userList = Array.isArray(users) ? users : [];
        
        // Load for create form
        const assigneeSelect = document.getElementById('task-assignee');
        if (assigneeSelect) {
            const currentValue = assigneeSelect.value;
            assigneeSelect.innerHTML = '<option value="">Brak</option>';
            userList.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                assigneeSelect.appendChild(option);
            });
            if (currentValue) {
                assigneeSelect.value = currentValue;
            }
        }
        
        // Load for edit form
        const editAssigneeSelect = document.getElementById('edit-task-assignee');
        if (editAssigneeSelect) {
            const currentValue = editAssigneeSelect.value;
            editAssigneeSelect.innerHTML = '<option value="">Brak</option>';
            userList.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                editAssigneeSelect.appendChild(option);
            });
            if (currentValue) {
                editAssigneeSelect.value = currentValue;
            }
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Load projects for task form
async function loadProjectsForTaskForm() {
    try {
        const projects = await window.WorklyAPI.request('/projects/');
        const projectList = projects.results || projects || [];
        const projectSelect = document.getElementById('task-project');
        
        if (projectSelect) {
            projectSelect.innerHTML = '<option value="">Wybierz projekt</option>';
            projectList.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = project.name;
                projectSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Load projects for edit form
async function loadProjectsForEditForm() {
    try {
        const projects = await window.WorklyAPI.request('/projects/');
        const projectList = projects.results || projects || [];
        const projectSelect = document.getElementById('edit-task-project');
        
        if (projectSelect) {
            const currentValue = projectSelect.value;
            projectSelect.innerHTML = '<option value="">Wybierz projekt</option>';
            projectList.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = project.name;
                projectSelect.appendChild(option);
            });
            // Restore previous value if it exists
            if (currentValue) {
                projectSelect.value = currentValue;
            }
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

// Setup task form
function setupTaskForm() {
    const form = document.getElementById('create-task-form');
    if (!form) return;
    
    // Load projects and users
    loadProjectsForTaskForm();
    loadUsersForTaskForm();
    
    // Clear errors on input change
    const titleInput = document.getElementById('task-title');
    const projectSelect = document.getElementById('task-project');
    
    if (titleInput) {
        titleInput.addEventListener('input', () => {
            clearTaskError('task-title', 'title-error-label');
        });
    }
    
    if (projectSelect) {
        projectSelect.addEventListener('change', () => {
            clearTaskError('task-project', 'project-error-label');
            // Load parent tasks when project is selected
            const projectId = projectSelect.value;
            if (projectId) {
                loadParentTasksForForm(projectId);
            }
        });
    }
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous errors
        clearTaskError('task-title', 'title-error-label');
        clearTaskError('task-project', 'project-error-label');
        
        let hasError = false;
        
        // Validate project
        const project = document.getElementById('task-project').value;
        if (!project) {
            showTaskError('task-project', 'project-error-label', 'Projekt jest wymagany');
            hasError = true;
        }
        
        // Validate title
        const title = document.getElementById('task-title').value.trim();
        if (!title) {
            showTaskError('task-title', 'title-error-label', 'Tytuł jest wymagany');
            hasError = true;
        }
        
        if (hasError) {
            return;
        }
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Convert empty strings to null for optional fields
        if (!data.parent) data.parent = null;
        if (!data.start_date) data.start_date = null;
        if (!data.end_date) data.end_date = null;
        if (!data.description) data.description = '';
        if (!data.assignee) data.assignee = null;
        
        // Convert to integers
        if (data.progress) data.progress = parseInt(data.progress);
        if (data.parent) data.parent = parseInt(data.parent);
        data.project = parseInt(data.project);
        
        try {
            await window.WorklyAPI.request('/tasks/', {
                method: 'POST',
                body: JSON.stringify(data),
            });
            
            document.getElementById('create-task-modal').close();
            form.reset();
            loadTasks();
        } catch (error) {
            alert('Błąd podczas tworzenia zadania: ' + error.message);
        }
    });
}

// Setup edit task form
function setupEditTaskForm() {
    const form = document.getElementById('edit-task-form');
    if (!form) return;
    
    // Clear errors on input change
    const titleInput = document.getElementById('edit-task-title');
    const projectSelect = document.getElementById('edit-task-project');
    
    if (titleInput) {
        titleInput.addEventListener('input', () => {
            clearTaskError('edit-task-title', 'edit-title-error-label');
        });
    }
    
    if (projectSelect) {
        projectSelect.addEventListener('change', () => {
            clearTaskError('edit-task-project', 'edit-project-error-label');
            // Load parent tasks when project is selected
            const projectId = projectSelect.value;
            const taskId = document.getElementById('edit-task-id').value;
            if (projectId) {
                loadParentTasksForEditForm(projectId, taskId);
            }
        });
    }
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const taskId = document.getElementById('edit-task-id').value;
        if (!taskId) {
            alert('Błąd: Brak ID zadania');
            return;
        }
        
        // Clear previous errors
        clearTaskError('edit-task-title', 'edit-title-error-label');
        clearTaskError('edit-task-project', 'edit-project-error-label');
        
        let hasError = false;
        
        // Validate project
        const project = document.getElementById('edit-task-project').value;
        if (!project) {
            showTaskError('edit-task-project', 'edit-project-error-label', 'Projekt jest wymagany');
            hasError = true;
        }
        
        // Validate title
        const title = document.getElementById('edit-task-title').value.trim();
        if (!title) {
            showTaskError('edit-task-title', 'edit-title-error-label', 'Tytuł jest wymagany');
            hasError = true;
        }
        
        if (hasError) {
            return;
        }
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Remove id from data (it's not part of the update)
        delete data.id;
        
        // Convert empty strings to null for optional fields
        if (!data.parent) data.parent = null;
        if (!data.start_date) data.start_date = null;
        if (!data.end_date) data.end_date = null;
        if (!data.description) data.description = '';
        if (!data.assignee) data.assignee = null;
        
        // Convert to integers
        if (data.progress) data.progress = parseInt(data.progress);
        if (data.parent) data.parent = parseInt(data.parent);
        data.project = parseInt(data.project);
        if (data.assignee) data.assignee = parseInt(data.assignee);
        
        try {
            await window.WorklyAPI.request(`/tasks/${taskId}/`, {
                method: 'PATCH',
                body: JSON.stringify(data),
            });
            
            document.getElementById('edit-task-modal').close();
            form.reset();
            loadTasks();
        } catch (error) {
            alert('Błąd podczas aktualizacji zadania: ' + error.message);
        }
    });
}

async function loadParentTasksForForm(projectId) {
    try {
        const tasks = await window.WorklyAPI.request(`/tasks/?project=${projectId}`);
        const taskList = tasks.results || tasks || [];
        const parentSelect = document.getElementById('task-parent');
        
        if (parentSelect) {
            // Clear existing options except first
            parentSelect.innerHTML = '<option value="">Brak (zadanie główne)</option>';
            
            // Add tasks without parent as options
            taskList.filter(t => !t.parent).forEach(task => {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = task.title;
                parentSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading parent tasks:', error);
    }
}

async function loadParentTasksForEditForm(projectId, excludeTaskId = null) {
    try {
        const tasks = await window.WorklyAPI.request(`/tasks/?project=${projectId}`);
        const taskList = tasks.results || tasks || [];
        const parentSelect = document.getElementById('edit-task-parent');
        
        if (parentSelect) {
            const currentValue = parentSelect.value;
            // Clear existing options except first
            parentSelect.innerHTML = '<option value="">Brak (zadanie główne)</option>';
            
            // Add tasks without parent as options, excluding the current task
            taskList.filter(t => !t.parent && t.id !== excludeTaskId).forEach(task => {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = task.title;
                parentSelect.appendChild(option);
            });
            // Restore previous value if it exists
            if (currentValue) {
                parentSelect.value = currentValue;
            }
        }
    } catch (error) {
        console.error('Error loading parent tasks:', error);
    }
}

// Load dependencies for a task (where this task is the successor)
async function loadDependenciesForTask(taskId, projectId) {
    try {
        // Get all dependencies where this task is the successor
        const dependencies = await window.WorklyAPI.request(`/dependencies/?successor=${taskId}`);
        const depsList = dependencies.results || dependencies || [];
        
        const depsContainer = document.getElementById('edit-dependencies-list');
        if (!depsContainer) return;
        
        if (depsList.length === 0) {
            depsContainer.innerHTML = '<p class="text-sm text-base-content/70">Brak zależności</p>';
            return;
        }
        
        // Load all tasks from project to get names
        const tasks = await window.WorklyAPI.request(`/tasks/?project=${projectId}`);
        const taskList = tasks.results || tasks || [];
        const tasksMap = new Map(taskList.map(t => [t.id, t]));
        
        depsContainer.innerHTML = depsList.map(dep => {
            const predecessor = tasksMap.get(dep.predecessor);
            const predName = predecessor ? predecessor.title : `Zadanie #${dep.predecessor}`;
            const typeLabels = {
                'FS': 'Koniec→Start',
                'SS': 'Start→Start',
                'FF': 'Koniec→Koniec',
                'SF': 'Start→Koniec'
            };
            
            return `
                <div class="flex items-center gap-2 p-2 bg-base-300 rounded" data-dependency-id="${dep.id}">
                    <span class="flex-1 text-sm">
                        <strong>${predName}</strong> 
                        <span class="badge badge-sm badge-info ml-2">${dep.type} (${typeLabels[dep.type] || dep.type})</span>
                        ${dep.lag_days ? `<span class="text-xs ml-2">Lag: ${dep.lag_days}d</span>` : ''}
                    </span>
                    <button type="button" class="btn btn-xs btn-error" onclick="removeDependency(${dep.id}, ${taskId})">Usuń</button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading dependencies:', error);
        const depsContainer = document.getElementById('edit-dependencies-list');
        if (depsContainer) {
            depsContainer.innerHTML = '<p class="text-sm text-error">Błąd podczas ładowania zależności</p>';
        }
    }
}

// Load tasks for dependency predecessor dropdown
async function loadTasksForDependencyDropdown(projectId, excludeTaskId) {
    try {
        const tasks = await window.WorklyAPI.request(`/tasks/?project=${projectId}`);
        const taskList = tasks.results || tasks || [];
        const predecessorSelect = document.getElementById('edit-dependency-predecessor');
        
        if (predecessorSelect) {
            predecessorSelect.innerHTML = '<option value="">Wybierz zadanie poprzedzające</option>';
            taskList.filter(t => t.id !== excludeTaskId).forEach(task => {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = task.title;
                predecessorSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading tasks for dependency dropdown:', error);
    }
}

// Add dependency
async function addDependency(taskId) {
    const predecessorSelect = document.getElementById('edit-dependency-predecessor');
    const typeSelect = document.getElementById('edit-dependency-type');
    const lagInput = document.getElementById('edit-dependency-lag');
    
    if (!predecessorSelect || !typeSelect || !lagInput) return;
    
    const predecessorId = predecessorSelect.value;
    const type = typeSelect.value;
    const lag = parseInt(lagInput.value) || 0;
    
    if (!predecessorId) {
        window.showAlertModal('Wybierz zadanie poprzedzające');
        return;
    }
    
    try {
        const dependencyData = {
            predecessor: parseInt(predecessorId),
            successor: taskId,
            type: type,
            lag_days: lag
        };
        
        await window.WorklyAPI.request('/dependencies/', {
            method: 'POST',
            body: JSON.stringify(dependencyData),
        });
        
        // Reload dependencies list
        const task = await window.WorklyAPI.request(`/tasks/${taskId}/`);
        await loadDependenciesForTask(taskId, task.project);
        
        // Clear form
        predecessorSelect.value = '';
        typeSelect.value = 'FS';
        lagInput.value = '0';
        
        // Reload tasks dropdown (in case we need to update it)
        await loadTasksForDependencyDropdown(task.project, taskId);
    } catch (error) {
        console.error('Error adding dependency:', error);
        let errorMessage = 'Błąd podczas dodawania zależności: ' + error.message;
        
        // Check for specific error messages
        if (error.message && error.message.includes('cykl')) {
            errorMessage = 'Nie można dodać zależności - spowodowałoby to cykl.';
        } else if (error.message && error.message.includes('projekt')) {
            errorMessage = 'Oba zadania muszą należeć do tego samego projektu.';
        } else if (error.message && error.message.includes('samego siebie')) {
            errorMessage = 'Zadanie nie może zależeć od samego siebie.';
        }
        
        window.showAlertModal(errorMessage);
    }
}

// Remove dependency
async function removeDependency(dependencyId, taskId) {
    window.showConfirmModal(
        'Czy na pewno chcesz usunąć tę zależność?',
        async () => {
            try {
                await window.WorklyAPI.request(`/dependencies/${dependencyId}/`, {
                    method: 'DELETE',
                });
                
                // Reload dependencies list
                const task = await window.WorklyAPI.request(`/tasks/${taskId}/`);
                await loadDependenciesForTask(taskId, task.project);
            } catch (error) {
                console.error('Error removing dependency:', error);
                window.showAlertModal('Błąd podczas usuwania zależności: ' + error.message);
            }
        }
    );
}

// Setup filter button
function setupFilterButton() {
    // Filter: My Tasks button
    const filterMyTasksBtn = document.getElementById('filter-my-tasks');
    if (filterMyTasksBtn) {
        // Remove any existing event listeners by cloning the button
        const newBtn = filterMyTasksBtn.cloneNode(true);
        filterMyTasksBtn.parentNode.replaceChild(newBtn, filterMyTasksBtn);
        
        // Set initial state if filter is active
        if (filterMyTasks) {
            newBtn.classList.add('btn-active');
            newBtn.classList.remove('btn-outline');
        } else {
            newBtn.classList.remove('btn-active');
            newBtn.classList.add('btn-outline');
        }
        
        newBtn.addEventListener('click', () => {
            filterMyTasks = !filterMyTasks;
            if (filterMyTasks) {
                newBtn.classList.add('btn-active');
                newBtn.classList.remove('btn-outline');
            } else {
                newBtn.classList.remove('btn-active');
                newBtn.classList.add('btn-outline');
            }
            loadTasks();
        });
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Wait for WorklyAPI to be available
    if (typeof window.WorklyAPI === 'undefined') {
        setTimeout(() => {
            if (typeof window.WorklyAPI !== 'undefined') {
                setupFilterButton();
                loadTasks();
                setupTaskForm();
                setupEditTaskForm();
            } else {
                console.error('WorklyAPI is not available');
                document.getElementById('tasks-content').innerHTML = `
                    <div class="alert alert-error">
                        <span>Błąd: WorklyAPI nie jest dostępne. Odśwież stronę.</span>
                    </div>
                `;
            }
        }, 100);
    } else {
        setupFilterButton();
        loadTasks();
        setupTaskForm();
        setupEditTaskForm();
    }
    
    // Setup status filter
    const statusFilter = document.getElementById('filter-status');
    if (statusFilter) {
        statusFilter.addEventListener('change', loadTasks);
    }
    
    // Setup search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(loadTasks, 500);
        });
    }
});

// Delete task function
async function deleteTask(taskId, event) {
    // Get task title from button data attribute
    const button = event ? event.target.closest('button') : null;
    const taskTitle = button ? button.getAttribute('data-task-title') || 'to zadanie' : 'to zadanie';
    
    window.showConfirmModal(
        `Czy na pewno chcesz usunąć zadanie "${taskTitle}"?`,
        async () => {
            try {
                await window.WorklyAPI.request(`/tasks/${taskId}/`, {
                    method: 'DELETE',
                });
                
                // Reload tasks
                loadTasks();
            } catch (error) {
                console.error('Error deleting task:', error);
                window.showAlertModal('Błąd podczas usuwania zadania: ' + error.message);
            }
        }
    );
}

