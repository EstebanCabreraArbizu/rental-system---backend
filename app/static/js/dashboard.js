document.addEventListener('DOMContentLoaded', function() {
    // Manejar navegación
    const dashboardLink = document.getElementById('dashboardLink');
    const publicacionesLink = document.getElementById('publicacionesLink');
    const dashboardSection = document.getElementById('dashboardSection');
    const publicacionesSection = document.getElementById('publicacionesSection');

    function toggleSections(showDashboard) {
        dashboardSection.style.display = showDashboard ? 'block' : 'none';
        publicacionesSection.style.display = showDashboard ? 'none' : 'block';
        
        dashboardLink.classList.toggle('active', showDashboard);
        publicacionesLink.classList.toggle('active', !showDashboard);
    }

    dashboardLink.addEventListener('click', function(e) {
        e.preventDefault();
        toggleSections(true);
    });

    publicacionesLink.addEventListener('click', function(e) {
        e.preventDefault();
        toggleSections(false);
    });

    // Inicializar gráficos
    initializeCharts();
}); 