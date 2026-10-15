//
// js/auth.js
//

'use strict';

// Alterna a visibilidade da senha no formulário de autenticação.
const loginForm = document.querySelector('[data-login-form]');
const passwordInput = loginForm?.querySelector('[name="password"]');
const passwordToggle = loginForm?.querySelector('[data-password-toggle]');

if (passwordInput && passwordToggle) {
    passwordToggle.addEventListener('click', () => {
        const shouldShowPassword = passwordInput.type === 'password';

        passwordInput.type = shouldShowPassword ? 'text' : 'password';
        passwordToggle.textContent = shouldShowPassword
            ? 'Ocultar'
            : 'Mostrar';
        passwordToggle.setAttribute(
            'aria-label',
            shouldShowPassword ? 'Ocultar senha' : 'Mostrar senha'
        );
        passwordToggle.setAttribute(
            'aria-pressed',
            shouldShowPassword.toString()
        );
    });
}

// Impede o envio quando os campos HTML obrigatórios não são válidos.
loginForm?.addEventListener('submit', (event) => {
    if (!loginForm.checkValidity()) {
        event.preventDefault();
        loginForm.reportValidity();
    }
});
