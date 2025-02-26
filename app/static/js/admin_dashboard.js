document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
});

function initializeCharts() {
    // Gráfico de usuarios por tipo
    const userTypeCtx = document.getElementById('userTypeChart').getContext('2d');
    new Chart(userTypeCtx, {
        type: 'doughnut',
        data: {
            labels: ['Clientes', 'Propietarios', 'Administradores'],
            datasets: [{
                data: [stats.total_clientes, stats.total_propietarios, stats.total_admins],
                backgroundColor: ['#3498DB', '#E74C3C', '#2ECC71']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Gráfico de actividad mensual
    const activityCtx = document.getElementById('activityChart').getContext('2d');
    new Chart(activityCtx, {
        type: 'line',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            datasets: [{
                label: 'Nuevos Usuarios',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: '#2C3E50',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function setupEventListeners() {
    // Implementar funcionalidad de filtros y acciones
}

function verDetallesUsuario(userId) {
    // Implementar vista de detalles
}

function editarUsuario(userId) {
    // Implementar edición de usuario
} 