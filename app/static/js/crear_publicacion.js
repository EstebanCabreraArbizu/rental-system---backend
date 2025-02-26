document.addEventListener('DOMContentLoaded', function() {
    // Manejar cambio de tipo de publicación
    const radioVivienda = document.getElementById('vivienda');
    const radioVehiculo = document.getElementById('vehiculo');
    const camposVivienda = document.getElementById('camposVivienda');
    const camposVehiculo = document.getElementById('camposVehiculo');

    function toggleCampos() {
		console.log('Toggle campos: vivienda.checked =', radioVivienda.checked);
        if (radioVivienda.checked) {
            camposVivienda.style.display = 'block';
            camposVehiculo.style.display = 'none';
        } else {
            camposVivienda.style.display = 'none';
            camposVehiculo.style.display = 'block';
        }
    }

    radioVivienda.addEventListener('change', toggleCampos);
    radioVehiculo.addEventListener('change', toggleCampos);

    // Cargar distritos
    const distritos = [
        'Cercado de Lima', 'San Juan de Lurigancho', 'San Martín de Porres',
        'Ate', 'Comas', 'Villa El Salvador', 'Villa María del Triunfo',
        'San Juan de Miraflores', 'Los Olivos', 'Santiago de Surco'
    ];

    const selectDistrito = document.getElementById('distrito');
    distritos.forEach(distrito => {
        const option = document.createElement('option');
        option.value = distrito;
        option.textContent = distrito;
        selectDistrito.appendChild(option);
    });

    // Preview de imágenes
    const inputImagenes = document.getElementById('imagenes');
    const previewContainer = document.getElementById('previewImagenes');
    const MAX_IMAGES = 5;
    let selectedFiles = [];

    inputImagenes.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        
        if (selectedFiles.length + files.length > MAX_IMAGES) {
            alert(`Solo puedes subir un máximo de ${MAX_IMAGES} imágenes`);
            return;
        }

        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                selectedFiles.push(file);
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'col-auto preview-container';
                    previewDiv.innerHTML = `
                        <img src="${e.target.result}" class="preview-image">
                        <span class="remove-image">&times;</span>
                    `;
                    
                    previewDiv.querySelector('.remove-image').addEventListener('click', function() {
                        const index = selectedFiles.indexOf(file);
                        if (index > -1) {
                            selectedFiles.splice(index, 1);
                        }
                        previewDiv.remove();
                    });
                    
                    previewContainer.appendChild(previewDiv);
                };
                
                reader.readAsDataURL(file);
            }
        });
    });

    // Manejar envío del formulario
    const form = document.getElementById('publicacionForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validar campos requeridos
        const requiredFields = [
            'titulo',
            'descripcion',
            'precio',
            'distrito',
            'direccion',
            'latitud',
            'longitud'
        ];

        for (const fieldId of requiredFields) {
            const field = document.getElementById(fieldId);
            if (!field.value.trim()) {
                alert(`El campo ${fieldId} es requerido`);
                field.focus();
                return;
            }
        }

        // Validar campos específicos según el tipo de publicación
        if (radioVivienda.checked) {
            const viviendaFields = [
                'tipoVivienda',
                'fechaConstruccion',
                'antiguedad',
                'dimensiones'
            ];

            for (const fieldId of viviendaFields) {
                const field = document.getElementById(fieldId);
                if (!field.value.trim()) {
                    alert(`El campo ${fieldId} es requerido`);
                    field.focus();
                    return;
                }
            }
        }

        const formData = new FormData();
        
        // Información básica de la publicación
        formData.append('tipo_publicacion', radioVivienda.checked ? 'vivienda' : 'vehiculo');
        formData.append('titulo', document.getElementById('titulo').value);
        formData.append('descripcion', document.getElementById('descripcion').value);
        formData.append('precio', document.getElementById('precio').value);
        formData.append('distrito', document.getElementById('distrito').value);
        formData.append('direccion', document.getElementById('direccion').value);
        formData.append('latitud', document.getElementById('latitud').value);
        formData.append('longitud', document.getElementById('longitud').value);

        // Imágenes
        const imagenes = document.getElementById('imagenes').files;
        for (let i = 0; i < imagenes.length; i++) {
            formData.append('imagenes[]', imagenes[i]);
        }

        if (radioVivienda.checked) {
            // Datos específicos de vivienda
            const fechaConstruccion = document.getElementById('fechaConstruccion').value;
            const antiguedad = document.getElementById('antiguedad').value;
            
            formData.append('fecha_construccion', fechaConstruccion);
            formData.append('antiguedad', antiguedad);
            formData.append('dimensiones', document.getElementById('dimensiones').value);
            formData.append('tipo_vivienda', document.getElementById('tipoVivienda').value);
            
            // Ambientes seleccionados
            const ambientes = document.querySelectorAll('input[name="ambientes[]"]:checked');
            ambientes.forEach(ambiente => {
                formData.append('ambientes[]', ambiente.value);
            });

            // Servicios seleccionados
            const servicios = document.querySelectorAll('input[name="servicios[]"]:checked');
            servicios.forEach(servicio => {
                formData.append('servicios[]', servicio.value);
            });
        } else {
            formData.append('tipo_vehiculo', document.getElementById('tipoVehiculo').value);
            formData.append('marca', document.getElementById('marca').value);
            formData.append('modelo', document.getElementById('modelo').value);
			formData.append('anio', document.getElementById('anio').value);
			formData.append('placa', document.getElementById('placa').value);
			formData.append('color', document.getElementById('color').value);
			formData.append('transmision', document.getElementById('transmision').value);
			formData.append('cant_combustible', document.getElementById('cantCombustible').value);
			formData.append('tipo_combustible', document.getElementById('tipoCombustible').value);
			formData.append('kilometraje', document.getElementById('kilometraje').value);
			formData.append('seguro', document.getElementById('seguro').value);
			// Equipamientos seleccionados
            const equipamientos = document.querySelectorAll('input[name="equipamientos[]"]:checked');
            equipamientos.forEach(equipamiento => {
                formData.append('equipamientos[]', equipamiento.value);
            });

        }

        // Agregar logs en consola
        console.log('Datos a enviar:', Object.fromEntries(formData));

        try {
            const response = await fetch('/owner/add_publication', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                alert('Publicación creada exitosamente');
                window.location.href = '/dashboard';
            } else {
                alert('Error al crear la publicación: ' + (data.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la publicación: ' + error.message);

        }
    });
}); 