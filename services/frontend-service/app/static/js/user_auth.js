(() => {
    'use strict';

    const registerForm = document.querySelector('[data-register-form]');
    const whatsappInput = registerForm?.querySelector('[data-whatsapp-mask]');

    /**
     * Remove os caracteres utilizados somente pela máscara visual.
     *
     * @param {string} value Valor atual do campo.
     * @returns {string} Valor contendo somente dígitos.
     */
    function whatsappDigits(value) {
        return value.replace(/\D/g, '');
    }

    /**
     * Formata o WhatsApp apresentado no cadastro do usuário.
     *
     * @param {string} value Valor atual do campo.
     * @returns {string} Número formatado para exibição.
     */
    function formatWhatsapp(value) {
        const digits = whatsappDigits(value);
        let formattedValue;

        if (digits.length === 0) {
            return '';
        }

        if (digits.length <= 2) {
            formattedValue = `(${digits}`;
        } else if (digits.length <= 7) {
            formattedValue = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
        } else {
            formattedValue = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
        }

        return whatsappInput.maxLength >= 0
            ? formattedValue.slice(0, whatsappInput.maxLength)
            : formattedValue;
    }

    if (registerForm && whatsappInput) {
        whatsappInput.value = formatWhatsapp(whatsappInput.value);

        whatsappInput.addEventListener('input', () => {
            whatsappInput.value = formatWhatsapp(whatsappInput.value);
        });

        registerForm.addEventListener('submit', () => {
            whatsappInput.value = whatsappDigits(whatsappInput.value);
        });
    }

    const passwordResetForm = document.querySelector(
        '[data-password-reset-form]'
    );

    passwordResetForm?.addEventListener('submit', (event) => {
        if (!passwordResetForm.checkValidity()) {
            event.preventDefault();
            passwordResetForm.reportValidity();
        }
    });

    const passwordResetConfirmForm = document.querySelector(
        '[data-password-reset-confirm-form]'
    );
    const newPasswordInput = passwordResetConfirmForm?.querySelector(
        '[name="new_password"]'
    );
    const confirmNewPasswordInput = passwordResetConfirmForm?.querySelector(
        '[name="confirm_new_password"]'
    );

    if (
        passwordResetConfirmForm
        && newPasswordInput
        && confirmNewPasswordInput
    ) {
        passwordResetConfirmForm.addEventListener('submit', (event) => {
            confirmNewPasswordInput.setCustomValidity(
                newPasswordInput.value === confirmNewPasswordInput.value
                    ? ''
                    : 'A confirmação deve ser igual à nova senha.'
            );

            if (!passwordResetConfirmForm.checkValidity()) {
                event.preventDefault();
                passwordResetConfirmForm.reportValidity();
            }
        });

        confirmNewPasswordInput.addEventListener('input', () => {
            confirmNewPasswordInput.setCustomValidity(
                newPasswordInput.value === confirmNewPasswordInput.value
                    ? ''
                    : 'A confirmação deve ser igual à nova senha.'
            );
        });
    }

    const currentUrl = new URL(window.location.href);
    const authenticationSucceeded = (
        currentUrl.searchParams.get('code') === 'USER_AUTHENTICATION_SUCCESS'
        || document.querySelector('[data-authentication-success]') !== null
    );

    if (!authenticationSucceeded) {
        return;
    }

    /**
     * Posiciona a página no topo após a autenticação.
     *
     * @returns {void}
     */
    function scrollToPageTop() {
        const previousScrollBehavior = document.documentElement.style.scrollBehavior;
        document.documentElement.style.scrollBehavior = 'auto';
        window.scrollTo(0, 0);
        document.documentElement.style.scrollBehavior = previousScrollBehavior;
    }

    if ('scrollRestoration' in window.history) {
        window.history.scrollRestoration = 'manual';
    }

    currentUrl.searchParams.delete('code');
    window.history.replaceState({}, '', currentUrl);

    scrollToPageTop();
    window.requestAnimationFrame(scrollToPageTop);
    window.addEventListener('pageshow', scrollToPageTop, { once: true });
})();
