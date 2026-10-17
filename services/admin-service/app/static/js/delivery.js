//
// js/delivery.js
//

'use strict';

/**
 * Aplica a máscara brasileira de CEP enquanto o usuário digita.
 *
 * @param {string} value Valor atual do campo.
 * @returns {string} CEP limitado a oito dígitos no formato 00000-000.
 */
function formatZipCode(value) {
    const digits = value.replace(/\D/g, '').slice(0, 8);

    if (digits.length <= 5) {
        return digits;
    }

    return `${digits.slice(0, 5)}-${digits.slice(5)}`;
}

document.querySelectorAll('[data-cep-input]').forEach((input) => {
    // Formata valores iniciais e também valores colados pelo usuário.
    input.value = formatZipCode(input.value);

    input.addEventListener('input', () => {
        input.value = formatZipCode(input.value);
    });
});
