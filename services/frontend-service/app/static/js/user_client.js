(() => {
    'use strict';

    const registerForm = document.querySelector('[data-register-form]');
    const whatsappInput = registerForm?.querySelector('[data-whatsapp-mask]');

    if (!registerForm || !whatsappInput) {
        return;
    }

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
     * Aplica a máscara visual e respeita o maxlength definido no campo.
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

    whatsappInput.value = formatWhatsapp(whatsappInput.value);

    whatsappInput.addEventListener('input', () => {
        whatsappInput.value = formatWhatsapp(whatsappInput.value);
    });

    registerForm.addEventListener('submit', () => {
        // A máscara é apenas visual. As validações continuam sob
        // responsabilidade dos atributos HTML e do formulário no backend.
        whatsappInput.value = whatsappDigits(whatsappInput.value);
    });
})();
