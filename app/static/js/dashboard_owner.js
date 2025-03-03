document.addEventListener('DOMContentLoaded', function () {
	const sections = ['dashboardSection', 'clientesSection', 'publicacionesSection']

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
	// Inicializar datos de publicaciones y estadísticas
const interesadosPorMes = {
	labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
	datasets: [{
		label: 'Interesados',
		data: [12, 19, 3, 5, 2, 3],
		borderColor: '#3498DB',
		tension: 0.1
	}]
};

// Configurar gráficos
new Chart(document.getElementById('tipoPublicacionChart'), {
	type: 'doughnut',
	data: tipoPublicacionData,
	options: {
		responsive: true,
		plugins: {
			legend: {
				position: 'bottom'
			}
		}
	}
});

new Chart(document.getElementById('interesadosChart'), {
	type: 'line',
	data: interesadosPorMes,
	options: {
		responsive: true,
		scales: {
			y: {
				beginAtZero: true
			}
		}
	}
});
cargarPublicaciones();
cargarEstadisticasInteresados();
});
// Función para cargar las publicaciones
function cargarPublicaciones() {
	fetch('/owner/publicaciones')
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				actualizarTablaPublicaciones(data.publicaciones);
			}
		})
		.catch(error => console.error('Error al cargar publicaciones: ', error));
}
// Función para actualizar la tabla de publicaciones en el dashboard
function actualizarTablaPublicaciones(publicaciones) {
	// Ejemplo: limpiar y reconstruir la tabla dentro de un contenedor (a adaptar según tu HTML)
	const tableBody = document.getElementById('publicacionesTable');
	if (tableBody) {
		tableBody.innerHTML = ''; // Limpiar la tabla
		publicaciones.forEach(pub => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
			<td>${pub.titulo}</td>
			<td>${pub.tipo_publicacion}</td>
			<td>S/. ${parseFloat(pub.precio_unitario).toFixed(2)}</td>
			<td>${pub.total_interesados}</td>
			<td>
				<span class="badge bg-${pub.estado === 'Activo' ? 'success' : 'secondary'}">
					${pub.estado}
				</span>
			</td>
			<td>
				<button class="btn btn-sm btn-primary" onclick="verDetallesPublicacion(${pub.id_publicacion})">
					<i class="fas fa-eye"></i> Ver más
				</button>
				<button class="btn btn-sm btn-danger" onclick="eliminarPublicacion(${pub.id_publicacion})">
					<i class="fas fa-trash"></i> Eliminar
				</button>
			</td>
		`;
			tableBody.appendChild(tr);
		});
	}
}

// Función para cargar estadísticas de interesados
function cargarEstadisticasInteresados() {
	fetch('/owner/estadisticas/interesados')
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				actualizarGraficoInteresados(data.datos);
			}
		})
		.catch(error => console.error('Error al cargar estadísticas:', error));
}



// Función para eliminar publicación
function eliminarPublicacion(id) {
	if (confirm('¿Estás seguro de que deseas eliminar esta publicación?')) {
		fetch(`/owner/delete/${id}`, { method: 'DELETE' })
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					cargarPublicaciones();
					alert(data.message);
				} else {
					alert('Error al eliminar la publicación: ' + data.error);
				}
			})
			.catch(error => {
				console.error('Error:', error);
				alert('Error de comunicación con el servidor.');
			});
	}
}
function verDetallesUsuario(id) {
	fetch(`/owner/usuario/${id}`)
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
	fetch(`/owner/publicacion/${id}`)
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


// Función para actualizar el gráfico de interesados usando los datos de la estadística
function actualizarGraficoInteresados(datos) {
	// Por ejemplo, actualizar un chart (si estás usando Chart.js, se puede llamar al método update())
	console.log("Actualizando gráfico de interesados...", datos);
}