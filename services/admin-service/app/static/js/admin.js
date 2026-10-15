(() => {
    'use strict';

    const currentYear = document.querySelector('[data-current-year]');

    if (currentYear) {
        currentYear.textContent = new Date().getFullYear().toString();
    }

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

    loginForm?.addEventListener('submit', (event) => {
        if (!loginForm.checkValidity()) {
            event.preventDefault();
            loginForm.reportValidity();
        }
    });

    const messageModal = document.querySelector('[data-message-modal]');

    if (messageModal && typeof messageModal.showModal === 'function') {
        messageModal.querySelector('[data-modal-close]')?.addEventListener(
            'click',
            () => messageModal.close()
        );

        messageModal.showModal();

        if (messageModal.hasAttribute('data-modal-clean-url')) {
            const cleanUrl = new URL(window.location.href);
            cleanUrl.searchParams.delete('code');
            window.history.replaceState({}, document.title, cleanUrl);
        }
    }

    const dashboardSidebar = document.querySelector(
        '[data-dashboard-sidebar]'
    );
    const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
    const sidebarOverlay = document.querySelector('[data-sidebar-overlay]');

    if (dashboardSidebar && sidebarToggle && sidebarOverlay) {
        sidebarToggle.addEventListener('click', () => {
            const isOpen = dashboardSidebar.classList.toggle('is-open');
            sidebarOverlay.classList.toggle('is-visible', isOpen);
            sidebarToggle.setAttribute('aria-expanded', isOpen.toString());
            document.body.classList.toggle('has-open-sidebar', isOpen);
        });

        sidebarOverlay.addEventListener('click', () => {
            dashboardSidebar.classList.remove('is-open');
            sidebarOverlay.classList.remove('is-visible');
            sidebarToggle.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('has-open-sidebar');
        });
    }
})();
