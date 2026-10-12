(() => {
    'use strict';

    const cardholderField = document.querySelector('[data-payment-cardholder]');
    const cardNumberField = document.querySelector('[data-payment-card-number]');
    const expirationField = document.querySelector(
        '[data-payment-card-expiration]'
    );
    const securityCodeField = document.querySelector(
        '[data-payment-card-security-code]'
    );
    const paymentForm = document.querySelector('[data-checkout-payment-form]');
    const paymentModal = document.querySelector(
        '[data-checkout-payment-modal]'
    );
    const addressModal = document.querySelector(
        '[data-checkout-address-modal]'
    );

    /**
     * Mantém somente letras e espaços e converte o nome para maiúsculas.
     *
     * @param {string} value - Valor atual do campo.
     * @returns {string} Nome formatado para impressão no cartão.
     */
    function formatCardholderName(value) {
        return value
            .replace(/[^\p{L}\s]/gu, '')
            .toLocaleUpperCase('pt-BR');
    }

    /**
     * Mantém até 16 dígitos e os separa em grupos de quatro.
     *
     * @param {string} value - Valor atual do campo.
     * @returns {string} Número do cartão mascarado.
     */
    function formatCardNumber(value) {
        const digits = value.replace(/\D/g, '').slice(0, 16);

        return digits.match(/.{1,4}/g)?.join(' ') ?? '';
    }

    /**
     * Mantém até quatro dígitos e insere a separação entre mês e ano.
     *
     * @param {string} value - Valor atual do campo.
     * @returns {string} Validade no formato MM/AA.
     */
    function formatCardExpiration(value) {
        const digits = value.replace(/\D/g, '').slice(0, 4);

        return digits.length > 2
            ? `${digits.slice(0, 2)}/${digits.slice(2)}`
            : digits;
    }

    /**
     * Mantém somente os três dígitos do código de segurança.
     *
     * @param {string} value - Valor atual do campo.
     * @returns {string} Código de segurança sanitizado.
     */
    function formatCardSecurityCode(value) {
        return value.replace(/\D/g, '').slice(0, 3);
    }

    /**
     * Aplica e mantém uma função de formatação em um campo.
     *
     * @param {HTMLInputElement|null} field - Campo que será formatado.
     * @param {(value: string) => string} formatter - Função de formatação.
     * @returns {void}
     */
    function bindFormatter(field, formatter) {
        if (!field) {
            return;
        }

        field.value = formatter(field.value);
        field.addEventListener('input', () => {
            field.value = formatter(field.value);
        });
    }

    /**
     * Localiza o primeiro campo de pagamento que ainda não está completo.
     *
     * A conferência considera somente os dados visuais do cartão. Os campos
     * ocultos pertencem à revalidação do checkout feita pelo backend e não
     * devem provocar o modal de preenchimento do cartão.
     *
     * @returns {HTMLInputElement|null} Primeiro campo incompleto ou `null`
     *     quando todos os dados de pagamento estiverem preenchidos.
     */
    function getFirstIncompletePaymentField() {
        const expectedCardDigits = (
            cardNumberField?.placeholder.match(/\d/g) ?? []
        ).length;
        const cardDigits = cardNumberField?.value.replace(/\D/g, '') ?? '';
        const expiration = expirationField?.value ?? '';
        const securityCode = securityCodeField?.value ?? '';

        if (!cardholderField?.value.trim()) {
            return cardholderField;
        }

        if (!expectedCardDigits || cardDigits.length !== expectedCardDigits) {
            return cardNumberField;
        }

        if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(expiration)) {
            return expirationField;
        }

        if (
            securityCode.length < securityCodeField.minLength
            || securityCode.length > securityCodeField.maxLength
        ) {
            return securityCodeField;
        }

        return null;
    }

    bindFormatter(cardholderField, formatCardholderName);
    bindFormatter(cardNumberField, formatCardNumber);
    bindFormatter(expirationField, formatCardExpiration);
    bindFormatter(securityCodeField, formatCardSecurityCode);

    if (paymentForm && paymentModal) {
        const paymentModalConfirmation = paymentModal.querySelector(
            '[data-checkout-payment-modal-confirm]'
        );
        let firstInvalidField = null;

        /**
         * Fecha o aviso e posiciona o cursor no primeiro campo inválido.
         *
         * @returns {void}
         */
        function closePaymentModal() {
            window.OciPizzaModal?.close(paymentModal);
            firstInvalidField?.focus();
        }

        /**
         * Impede o envio incompleto e apresenta o aviso de validação.
         *
         * @param {SubmitEvent} event - Evento de submissão do checkout.
         * @returns {void}
         */
        function validatePaymentForm(event) {
            firstInvalidField = getFirstIncompletePaymentField();

            if (!firstInvalidField) {
                return;
            }

            event.preventDefault();
            window.OciPizzaModal?.open(paymentModal);
        }

        // A validação roda na fase de captura para cancelar formulários
        // incompletos antes que o bloqueador global processe a submissão.
        paymentForm.addEventListener('submit', validatePaymentForm, {
            capture: true
        });
        paymentModalConfirmation.addEventListener('click', closePaymentModal);
    }

    if (addressModal) {
        const confirmationButton = addressModal.querySelector(
            '[data-checkout-address-modal-confirm]'
        );
        const redirectUrl = addressModal.dataset.redirectUrl;

        /**
         * Redireciona o usuário para gerenciar seus endereços.
         *
         * @returns {void}
         */
        function redirectToProfile() {
            window.location.assign(redirectUrl);
        }

        // O modal representa uma condição obrigatória do checkout e, por isso,
        // é aberto assim que a página termina de carregar.
        window.OciPizzaModal?.open(addressModal);
        confirmationButton.addEventListener('click', redirectToProfile);

        // Impede fechar o aviso com Esc e permanecer em um checkout que não pode
        // ser concluído. A única ação disponível leva ao gerenciamento do perfil.
        addressModal.addEventListener('cancel', (event) => {
            event.preventDefault();
        });
    }
})();
