//
// js/orders.js
//

'use strict';

// Solicita confirmação antes de excluir um pedido.
const deleteOrderForm = document.querySelector('[data-delete-order-form]');
const deleteOrderModal = document.querySelector('[data-delete-order-modal]');

if (
    deleteOrderForm &&
    deleteOrderModal &&
    typeof deleteOrderModal.showModal === 'function'
) {
    const confirmDeleteOrder = deleteOrderModal.querySelector(
        '[data-confirm-delete-order]'
    );
    const cancelDeleteOrder = deleteOrderModal.querySelector(
        '[data-cancel-delete-order]'
    );

    deleteOrderForm.addEventListener('submit', (event) => {
        event.preventDefault();
        deleteOrderModal.showModal();
    });

    cancelDeleteOrder?.addEventListener('click', () => {
        deleteOrderModal.close();
    });

    confirmDeleteOrder?.addEventListener('click', () => {
        confirmDeleteOrder.disabled = true;
        window.AdminInteractionLock?.lock();
        deleteOrderForm.submit();
    });
}
