//
// js/modals.js
//

'use strict';

// Exibe mensagens retornadas após um redirect e remove o código da URL.
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
