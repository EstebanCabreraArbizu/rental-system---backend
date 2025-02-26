document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    const radioVivienda = document.getElementById('vivienda');
    const radioVehiculo = document.getElementById('vehiculo');
    const camposVivienda = document.getElementById('camposVivienda');
    const camposVehiculo = document.getElementById('camposVehiculo');
    const form = document.getElementById('publicacionForm');
    let selectedFiles = [];
    const MAX_IMAGES = 5;

    // Función para alternar entre campos de vivienda y vehículo
    function toggleCampos() {
        if (radioVivienda.checked) {
            camposVivienda.style.display = 'block';
            camposVehiculo.style.display = 'none';
        } else {
            camposVivienda.style.display = 'none';
            camposVehiculo.style.display = 'block';
        }
    }

    // Event listeners para los radio buttons
    radioVivienda.addEventListener('change', toggleCampos);
    radioVehiculo.addEventListener('change', toggleCampos);

    // Inicializar distritos
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

    // Manejo de imágenes
    const inputImagenes = document.getElementById('imagenes');
    const previewContainer = document.getElementById('previewImagenes');

    function handleImagePreview(files) {
        if (selectedFiles.length + files.length > MAX_IMAGES) {
            alert(`Solo puedes subir un máximo de ${MAX_IMAGES} imágenes`);
            return;
        }

        Array.from(files).forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewDiv = createPreviewElement(e.target.result, file);
                    previewContainer.appendChild(previewDiv);
                };
                reader.readAsDataURL(file);
                selectedFiles.push(file);
            }
        });
    }

    function createPreviewElement(src, file) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'col-auto preview-container';
        previewDiv.innerHTML = `
            <img src="${src}" class="preview-image">
            <span class="remove-image">&times;</span>
        `;
        
        previewDiv.querySelector('.remove-image').addEventListener('click', () => {
            const index = selectedFiles.indexOf(file);
            if (index > -1) {
                selectedFiles.splice(index, 1);
            }
            previewDiv.remove();
        });
        
        return previewDiv;
    }

    inputImagenes.addEventListener('change', (e) => handleImagePreview(e.target.files));

    // Validación de campos
    function validateRequiredFields() {
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
                return false;
            }
        }

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
                    return false;
                }
            }
        }

        return true;
    }

    // Manejo del envío del formulario
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!validateRequiredFields()) {
            return;
        }

        const formData = new FormData();
        
        // Información básica
        formData.append('tipo_publicacion', radioVivienda.checked ? 'vivienda' : 'vehiculo');
        formData.append('titulo', document.getElementById('titulo').value);
        formData.append('descripcion', document.getElementById('descripcion').value);
        formData.append('precio', document.getElementById('precio').value);
        formData.append('distrito', document.getElementById('distrito').value);
        formData.append('direccion', document.getElementById('direccion').value);
        formData.append('latitud', document.getElementById('latitud').value);
        formData.append('longitud', document.getElementById('longitud').value);

        // Imágenes
        selectedFiles.forEach(file => {
            formData.append('imagenes[]', file);
        });

        // Datos específicos según el tipo
        if (radioVivienda.checked) {
            appendViviendaData(formData);
        } else {
            appendVehiculoData(formData);
        }

        try {
            const response = await fetch('/crear_publicacion', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                alert('Publicación creada exitosamente');
                window.location.href = '/dashboard_propietario#publicaciones';
            } else {
                alert('Error al crear la publicación: ' + (data.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la publicación');
        }
    }

    function appendViviendaData(formData) {
        formData.append('fecha_construccion', document.getElementById('fechaConstruccion').value);
        formData.append('antiguedad', document.getElementById('antiguedad').value);
        formData.append('dimensiones', document.getElementById('dimensiones').value);
        formData.append('tipo_vivienda', document.getElementById('tipoVivienda').value);
        
        // Ambientes y servicios
        document.querySelectorAll('input[name="ambientes[]"]:checked').forEach(ambiente => {
            formData.append('ambientes[]', ambiente.value);
        });

        document.querySelectorAll('input[name="servicios[]"]:checked').forEach(servicio => {
            formData.append('servicios[]', servicio.value);
        });
    }

    function appendVehiculoData(formData) {
        formData.append('tipo_vehiculo', document.getElementById('tipoVehiculo').value);
        formData.append('marca', document.getElementById('marca').value);
        formData.append('modelo', document.getElementById('modelo').value);
        formData.append('anio', document.getElementById('anio').value);
        formData.append('placa', document.getElementById('placa').value);
        formData.append('color', document.getElementById('color').value);
        formData.append('transmision', document.getElementById('transmision').value);
        formData.append('cantCombustible', document.getElementById('cantCombustible').value);
        formData.append('tipoCombustible', document.getElementById('tipoCombustible').value);
        formData.append('kilometraje', document.getElementById('kilometraje').value);
    }

    // Event listener para el formulario
    form.addEventListener('submit', handleSubmit);
}); 