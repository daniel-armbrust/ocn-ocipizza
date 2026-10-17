// js/users.js

'use strict';

const whatsappInputs = document.querySelectorAll('[data-whatsapp-mask]');

// Remove os caracteres utilizados somente pela máscara visual.
function whatsappDigits(value) {
    return value.replace(/\D/g, '').slice(0, 11);
}

// Formata o WhatsApp para exibição e preserva somente os onze dígitos
// durante a submissão do formulário.
function formatWhatsapp(value) {
    const digits = whatsappDigits(value);

    if (digits.length <= 2) {
        return digits ? `(${digits}` : '';
    }

    if (digits.length <= 7) {
        return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    }

    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}

whatsappInputs.forEach((input) => {
    input.value = formatWhatsapp(input.value);
    input.addEventListener('input', () => {
        input.value = formatWhatsapp(input.value);
    });

    input.form?.addEventListener('submit', () => {
        input.value = whatsappDigits(input.value);
    });
});

// Solicita confirmação antes de excluir um usuário.
const deleteUserForm = document.querySelector('[data-delete-user-form]');
const deleteUserModal = document.querySelector('[data-delete-user-modal]');

if (
    deleteUserForm &&
    deleteUserModal &&
    typeof deleteUserModal.showModal === 'function'
) {
    const confirmDeleteUser = deleteUserModal.querySelector(
        '[data-confirm-delete-user]'
    );
    const cancelDeleteUser = deleteUserModal.querySelector(
        '[data-cancel-delete-user]'
    );

    deleteUserForm.addEventListener('submit', (event) => {
        event.preventDefault();
        deleteUserModal.showModal();
    });

    cancelDeleteUser?.addEventListener('click', () => {
        deleteUserModal.close();
    });

    confirmDeleteUser?.addEventListener('click', () => {
        confirmDeleteUser.disabled = true;
        window.AdminInteractionLock?.lock();
        deleteUserForm.submit();
    });
}
