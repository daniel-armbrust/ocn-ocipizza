//
// js/kitchen.js
//

'use strict';

// Solicita confirmação antes de iniciar o preparo de um pedido.
const startPreparationForm = document.querySelector(
    '[data-start-preparation-form]'
);
const startPreparationModal = document.querySelector(
    '[data-start-preparation-modal]'
);

if (
    startPreparationForm &&
    startPreparationModal &&
    typeof startPreparationModal.showModal === 'function'
) {
    const confirmPreparation = startPreparationModal.querySelector(
        '[data-confirm-preparation]'
    );
    const cancelPreparation = startPreparationModal.querySelector(
        '[data-cancel-preparation]'
    );

    startPreparationForm.addEventListener('submit', (event) => {
        event.preventDefault();
        startPreparationModal.showModal();
    });

    cancelPreparation?.addEventListener('click', () => {
        startPreparationModal.close();
    });

    confirmPreparation?.addEventListener('click', () => {
        confirmPreparation.disabled = true;
        window.AdminInteractionLock?.lock();
        startPreparationForm.submit();
    });
}

// Solicita confirmação antes de marcar um pedido como pronto.
const markReadyForm = document.querySelector('[data-mark-ready-form]');
const markReadyModal = document.querySelector('[data-mark-ready-modal]');

if (
    markReadyForm &&
    markReadyModal &&
    typeof markReadyModal.showModal === 'function'
) {
    const confirmReady = markReadyModal.querySelector(
        '[data-confirm-ready]'
    );
    const cancelReady = markReadyModal.querySelector(
        '[data-cancel-ready]'
    );

    markReadyForm.addEventListener('submit', (event) => {
        event.preventDefault();
        markReadyModal.showModal();
    });

    cancelReady?.addEventListener('click', () => {
        markReadyModal.close();
    });

    confirmReady?.addEventListener('click', () => {
        confirmReady.disabled = true;
        window.AdminInteractionLock?.lock();
        markReadyForm.submit();
    });
}
