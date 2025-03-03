// Variables para manejar los pasos
const steps = document.querySelectorAll('.step');
let currentStep = 0;

// Función para mostrar el paso actual
function showStep(index) {
	steps.forEach((step, i) => {
		if (i === index) {
			step.classList.add('active');
		} else {
			step.classList.remove('active');
		}
	});
	currentStep = index;
}

// Función para validar el formulario
function validateForm(step) {
	const inputs = steps[step].querySelectorAll('input, select');
	let isValid = true;

	inputs.forEach(input => {
		if (input.hasAttribute('required') && !input.value) {
			isValid = false;
			input.classList.add('is-invalid');
		} else {
			input.classList.remove('is-invalid');
		}
	});

	return isValid;
}

// Función para pasar al siguiente paso
function nextStep() {
	if (!validateForm(currentStep)) {
		alert('Por favor, complete todos los campos requeridos.');
		return;
	}

	if (currentStep === 0) {
		// Validación específica para el paso 1
		const contrasenia = document.getElementById('contrasenia').value;
		const confirmContrasenia = document.getElementById('confirmContrasenia').value;

		if (contrasenia !== confirmContrasenia) {
			alert('Las contraseñas no coinciden');
			return;
		}
	}

	if (currentStep < steps.length - 1) {
		showStep(currentStep + 1);
	}
}

// Función para retroceder al paso anterior
function prevStep() {
	if (currentStep > 0) {
		showStep(currentStep - 1);
	}
}

// Previsualizar la imagen de perfil
document.getElementById('imagen').addEventListener('change', function (e) {
	const file = e.target.files[0];
	if (file) {
		const reader = new FileReader();
		reader.onload = function (event) {
			document.getElementById('avatarPreview').src = event.target.result;
		}
		reader.readAsDataURL(file);
	}
});

// Manejo del envío del formulario
document.getElementById('registerForm').addEventListener('submit', function (e) {
	e.preventDefault();

	if (!validateForm(currentStep)) {
		alert('Por favor, complete todos los campos requeridos.');
		return;
	}

	// Crear FormData para enviar los datos incluyendo la imagen
	const formData = new FormData(this);

	// Enviar el formulario
	fetch(this.action, {
		method: 'POST',
		body: formData
	})
		.then(response => {
			if (response.redirected) {
				window.location.href = response.url;
			} else {
				return response.text();
			}
		})
		.then(data => {
			if (data) {
				try {
					const result = JSON.parse(data);
					if (result.error) {
						alert(result.error);
					} else if (result.success) {
						window.location.href = result.redirect;
					}
				} catch (e) {
					// Si no es JSON, probablemente sea HTML
					document.open();
					document.write(data);
					document.close();
				}
			}
		})
		.catch(error => {
			console.error('Error:', error);
			alert('Ocurrió un error al procesar el registro');
		});
});