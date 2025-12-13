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
        
        console.log('Loading tasks from:', url);
        const response = await window.WorklyAPI.request(url);
        console.log('Tasks response:', response);
        
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
                                <button class="btn btn-sm btn-ghost" onclick="editTask(${task.id})">Edytuj</button>
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
        document.getElementById('edit-task-project').value = task.project || '';
        
        // Load parent tasks for the project
        if (task.project) {
            await loadParentTasksForEditForm(task.project, task.id);
            document.getElementById('edit-task-parent').value = task.parent || '';
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

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check URL parameter for auto-filtering "My Tasks"
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('my_tasks') === 'true') {
        filterMyTasks = true;
    }
    
    // Wait for WorklyAPI to be available
    if (typeof window.WorklyAPI === 'undefined') {
        setTimeout(() => {
            if (typeof window.WorklyAPI !== 'undefined') {
                loadTasks();
                setupTaskForm();
                setupFilterButton();
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
        loadTasks();
        setupTaskForm();
        setupEditTaskForm();
        setupFilterButton();
    }
});

// Setup filter button
function setupFilterButton() {
    // Filter: My Tasks button
    const filterMyTasksBtn = document.getElementById('filter-my-tasks');
    if (filterMyTasksBtn) {
        // Set initial state if filter is active
        if (filterMyTasks) {
            filterMyTasksBtn.classList.add('btn-active');
            filterMyTasksBtn.classList.remove('btn-outline');
        } else {
            filterMyTasksBtn.classList.remove('btn-active');
            filterMyTasksBtn.classList.add('btn-outline');
        }
        
        filterMyTasksBtn.addEventListener('click', () => {
            filterMyTasks = !filterMyTasks;
            if (filterMyTasks) {
                filterMyTasksBtn.classList.add('btn-active');
                filterMyTasksBtn.classList.remove('btn-outline');
            } else {
                filterMyTasksBtn.classList.remove('btn-active');
                filterMyTasksBtn.classList.add('btn-outline');
                // Remove my_tasks parameter from URL when filter is turned off
                const url = new URL(window.location);
                url.searchParams.delete('my_tasks');
                window.history.replaceState({}, '', url);
            }
            loadTasks();
        });
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check URL parameter for auto-filtering "My Tasks"
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('my_tasks') === 'true') {
        filterMyTasks = true;
    }
    
    // Wait for WorklyAPI to be available
    if (typeof window.WorklyAPI === 'undefined') {
        setTimeout(() => {
            if (typeof window.WorklyAPI !== 'undefined') {
                loadTasks();
                setupTaskForm();
                setupFilterButton();
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
        loadTasks();
        setupTaskForm();
        setupEditTaskForm();
        setupFilterButton();
    }
    
    document.getElementById('filter-status').addEventListener('change', loadTasks);
    
    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(loadTasks, 500);
    });
});

