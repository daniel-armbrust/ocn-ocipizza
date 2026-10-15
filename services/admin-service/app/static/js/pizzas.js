//
// js/pizzas.js
//

'use strict';

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
});

/**
 * Formata os dígitos de um campo como valor monetário brasileiro.
 *
 * @param {string} value Valor atual do campo.
 * @returns {string} Valor formatado em reais.
 */
function formatCurrency(value) {
    const digits = value.replace(/\D/g, '');

    if (!digits) {
        return '';
    }

    const cents = Number.parseInt(digits, 10);
    return currencyFormatter.format(cents / 100);
}

/**
 * Converte o valor visual para o formato decimal aceito pelo backend.
 *
 * @param {string} value Valor monetário formatado.
 * @returns {string} Valor decimal usando ponto como separador.
 */
function normalizeCurrency(value) {
    const digits = value.replace(/\D/g, '');

    if (!digits) {
        return '';
    }

    return (Number.parseInt(digits, 10) / 100).toFixed(2);
}

document.querySelectorAll('[data-money-input]').forEach((input) => {
    // Formata valores já preenchidos, como ocorre no formulário de edição.
    input.value = formatCurrency(input.value);

    input.addEventListener('input', () => {
        input.value = formatCurrency(input.value);
    });

    // O formulário envia o valor decimal, e não o texto com `R$`.
    input.form?.addEventListener('submit', () => {
        input.value = normalizeCurrency(input.value);
    });
});

// Solicita confirmação antes de salvar alterações na pizza.
const updatePizzaForm = document.querySelector('[data-update-pizza-form]');
const updatePizzaModal = document.querySelector('[data-update-pizza-modal]');

if (
    updatePizzaForm &&
    updatePizzaModal &&
    typeof updatePizzaModal.showModal === 'function'
) {
    const confirmUpdatePizza = updatePizzaModal.querySelector(
        '[data-confirm-update-pizza]'
    );
    const cancelUpdatePizza = updatePizzaModal.querySelector(
        '[data-cancel-update-pizza]'
    );

    updatePizzaForm.addEventListener('submit', (event) => {
        event.preventDefault();
        updatePizzaModal.showModal();
    });

    cancelUpdatePizza?.addEventListener('click', () => {
        updatePizzaModal.close();
    });

    confirmUpdatePizza?.addEventListener('click', () => {
        confirmUpdatePizza.disabled = true;
        window.AdminInteractionLock?.lock();
        updatePizzaForm.submit();
    });
}

// Solicita confirmação antes de excluir a pizza.
const deletePizzaForm = document.querySelector('[data-delete-pizza-form]');
const deletePizzaModal = document.querySelector('[data-delete-pizza-modal]');

if (
    deletePizzaForm &&
    deletePizzaModal &&
    typeof deletePizzaModal.showModal === 'function'
) {
    const confirmDeletePizza = deletePizzaModal.querySelector(
        '[data-confirm-delete-pizza]'
    );
    const cancelDeletePizza = deletePizzaModal.querySelector(
        '[data-cancel-delete-pizza]'
    );

    deletePizzaForm.addEventListener('submit', (event) => {
        event.preventDefault();
        deletePizzaModal.showModal();
    });

    cancelDeletePizza?.addEventListener('click', () => {
        deletePizzaModal.close();
    });

    confirmDeletePizza?.addEventListener('click', () => {
        confirmDeletePizza.disabled = true;
        window.AdminInteractionLock?.lock();
        deletePizzaForm.submit();
    });
}
