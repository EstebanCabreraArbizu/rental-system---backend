function togglePassword() {
	const passwordInput = document.getElementById('password');
	const icon = document.querySelector('.fa-eye, .fa-eye-slash');

	if (passwordInput.type === 'password') {
		passwordInput.type = 'text';
		icon.classList.replace('fa-eye', 'fa-eye-slash');
	} else {
		passwordInput.type = 'password';
		icon.classList.replace('fa-eye-slash', 'fa-eye');
	}
}

document.getElementById('loginForm').addEventListener('submit', function (e) {
	const submitBtn = document.getElementById('submitBtn');
	submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i>Iniciando sesión...';
	submitBtn.disabled = true;
});