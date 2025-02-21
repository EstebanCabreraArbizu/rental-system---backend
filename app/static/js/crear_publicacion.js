document.addEventListener('DOMContentLoaded', function() {
    // Manejar cambio de tipo de publicación
    const radioVivienda = document.getElementById('vivienda');
    const radioVehiculo = document.getElementById('vehiculo');
    const camposVivienda = document.getElementById('camposVivienda');
    const camposVehiculo = document.getElementById('camposVehiculo');

    function toggleCampos() {
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

        const formData = new FormData();
        formData.append('tipo_publicacion', radioVivienda.checked ? 'vivienda' : 'vehiculo');
        formData.append('titulo', document.getElementById('titulo').value);
        formData.append('descripcion', document.getElementById('descripcion').value);
        formData.append('precio', document.getElementById('precio').value);
        formData.append('distrito', document.getElementById('distrito').value);
        formData.append('direccion', document.getElementById('direccion').value);

        if (radioVivienda.checked) {
            formData.append('tipo_vivienda', document.getElementById('tipoVivienda').value);
            formData.append('habitaciones', document.getElementById('habitaciones').value);
            formData.append('banos', document.getElementById('banos').value);
        } else {
            formData.append('tipo_vehiculo', document.getElementById('tipoVehiculo').value);
            formData.append('marca', document.getElementById('marca').value);
            formData.append('modelo', document.getElementById('modelo').value);
        }

        selectedFiles.forEach(file => {
            formData.append('imagenes[]', file);
        });

        // Agregar logs en consola
        console.log('Datos a enviar:', Object.fromEntries(formData));

        try {
            const response = await fetch('/crear_publicacion', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                alert('Publicación creada exitosamente');
                window.location.href = '/dashboard_propietario';
            } else {
                alert('Error al crear la publicación: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la publicación');
        }
    });
}); 