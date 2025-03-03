document.addEventListener('DOMContentLoaded', function () {
	const sections = ['dashboard', 'usuarios', 'publicaciones']

	function showSection(sectionId) {
		sections.forEach(function (id) {
			document.getElementById(id).style.display = (id == sectionId) ? 'block' : 'none';
		})
	}
	const sidebarLinks = document.querySelectorAll('.sidebar a.nav-link');
	sidebarLinks.forEach(function (link) {
		link.addEventListener('click', function (e) {
			const href = this.getAttribute('href');
			if (href.startsWith('#')) {
				e.preventDefault();
				let target = this.getAttribute('href').substr(1);
				showSection(target);

				sidebarLinks.forEach(link => link.classList.remove('active'));
				this.classList.add('active');
			}
		});
	});
	initCharts();
	initDarkMode();
	initSidebar();
});
// Sidebar Toggle
function initSidebar() {
	const sidebarToggle = document.getElementById('sidebarToggle');
	const sidebar = document.querySelector('.sidebar');
	
	sidebarToggle.addEventListener('click', () => {
		sidebar.classList.toggle('active');
	});
}

// Dark Mode
function initDarkMode() {
	const darkModeToggle = document.getElementById('darkModeToggle');
	darkModeToggle.addEventListener('click', () => {
		document.body.classList.toggle('dark-mode');
		const icon = darkModeToggle.querySelector('i');
		icon.classList.toggle('fa-moon');
		icon.classList.toggle('fa-sun');
	});
}

// CRUD Functions
function editarUsuario(id) {
	fetch(`/usuario/${id}`)
		.then(response => response.json())
		.then(data => {
			document.getElementById('editUserId').value = id;
			document.getElementById('editNombre').value = data.nombre;
			document.getElementById('editCorreo').value = data.correo;
			new bootstrap.Modal(document.getElementById('editUserModal')).show();
		});
}

function eliminarUsuario(id) {
	if (confirm('¿Está seguro de eliminar este usuario?')) {
		fetch(`/usuario/eliminar/${id}`, {
			method: 'POST'
		})
		.then(response => response.json())
		.then(result => {
			if (result.success) {
				location.reload();
			} else {
				alert('Error al eliminar usuario');
			}
		});
	}
}
function verDetallesUsuario(id) {
   fetch(`/admin/usuario/${id}`)
	   .then(response => response.json())
	   .then(data => {
		   const modal = new bootstrap.Modal(document.getElementById('userDetailsModal'));
		   const userDetails = document.querySelector('.user-details');
		   
		   // Actualizar avatar
		   document.getElementById('userAvatar').src = data.imagen_url || 'https://i.pravatar.cc/150';
		   
		   // Construir detalles del usuario
		   userDetails.innerHTML = `
			   <div class="card border-0">
				   <div class="card-body p-0">
					   <h4 class="mb-1">${data.nombre}</h4>
					   <p class="text-muted mb-3">
						   <span class="badge bg-${data.tipo_usuario === 'Cliente' ? 'primary' : 'success'}">
							   ${data.tipo_usuario}
						   </span>
					   </p>
					   
					   <div class="info-group mb-3">
						   <h6 class="text-uppercase text-muted mb-2">Información Personal</h6>
						   <div class="mb-2">
							   <strong><i class="fas fa-envelope me-2"></i>Email:</strong>
							   <span class="ms-2">${data.correo}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-phone me-2"></i>Teléfono:</strong>
							   <span class="ms-2">${data.telefono || 'No especificado'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-id-card me-2"></i>Documento:</strong>
							   <span class="ms-2">${data.doc_identidad || 'No especificado'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-map-marker-alt me-2"></i>Dirección:</strong>
							   <span class="ms-2">${data.direccion || 'No especificada'}</span>
						   </div>
					   </div>
					   <div class="info-group mb-3">
						   <h6 class="text-uppercase text-muted mb-2">Detalles de la Cuenta</h6>
						   <div class="mb-2">
							   <strong><i class="fas fa-calendar me-2"></i>Fecha de registro:</strong>
							   <span class="ms-2">${new Date(data.fecha_ingreso).toLocaleDateString()}</span>
						   </div>
						   ${data.preferencias ? `
							   <div class="mb-2">
								   <strong><i class="fas fa-heart me-2"></i>Preferencias:</strong>
								   <span class="ms-2">${data.preferencias}</span>
							   </div>
						   ` : ''}
					   </div>
				   </div>
			   </div>
		   `;
		   
		   modal.show();
	   })
	   .catch(error => {
		   console.error('Error:', error);
		   alert('Error al cargar los detalles del usuario');
	   });
}
function verDetallesPublicacion(id) {
   fetch(`/admin/publicacion/${id}`)
	   .then(response => response.json())
	   .then(data => {
		   const modal = new bootstrap.Modal(document.getElementById('publicationDetailsModal'));
		   const publicationDetails = document.querySelector('.publication-details');
		   
		   // Actualizar avatar
		   document.getElementById('publicationAvatar').src = data.imagenes || 'https://i.pravatar.cc/150';
		   
		   // Construir detalles del usuario
		   publicationDetails.innerHTML = `
			   <div class="card border-0">
				   <div class="card-body p-0">
					   <h4 class="mb-1">${data.titulo}</h4>
					   
					   <div class="info-group mb-3">
						   <h6 class="text-uppercase text-muted mb-2">Información de la publicación</h6>
						   <div class="mb-2">
							   <strong><i class="fas fa-info-circle me-2"></i>Descripción:</strong>
							   <span class="ms-2">${data.descripcion}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-dollar-sign me-2"></i>Precio unitario:</strong>
							   <span class="ms-2">${data.precio_unitario || 'No especificado'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-map me-2"></i>Distrito:</strong>
							   <span class="ms-2">${data.distrito || 'No especificado'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-location-dot me-2"></i>Dirección:</strong>
							   <span class="ms-2">${data.direccion || 'No especificada'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-compass me-2"></i>Latitud:</strong>
							   <span class="ms-2">${data.latitud || 'No especificada'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-compass me-2"></i>Longitud:</strong>
							   <span class="ms-2">${data.longitud || 'No especificada'}</span>
						   </div>
						   <div class="mb-2">
							   <strong><i class="fas fa-toggle-on me-2"></i>Estado:</strong>
							   <span class="ms-2">${data.estado || 'No especificada'}</span>
						   </div>
					   </div>
					   <div class="info-group mb-3">
						   <h6 class="text-uppercase text-muted mb-2">Detalles de la publicación: </h6>
						   <div class="mb-2">
							   <strong><i class="fas fa-calendar me-2"></i>Fecha de publicación:</strong>
							   <span class="ms-2">${new Date(data.fecha_publicacion).toLocaleDateString()}</span>
						   </div>
					   </div>
				   </div>
			   </div>
		   `;
		   
		   modal.show();
	   })
	   .catch(error => {
		   console.error('Error:', error);
		   alert('Error al cargar los detalles del usuario');
	   });
}