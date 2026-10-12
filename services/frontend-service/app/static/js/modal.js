/*
 * Controlador global dos modais da aplicação.
 *
 * Modais declarados com `data-app-modal` podem ser abertos pelos templates ou
 * por scripts específicos sem duplicar a lógica de fechamento e acessibilidade.
 */
(function () {
    'use strict';

    /**
     * Abre um elemento dialog pelo padrão visual da aplicação.
     *
     * @param {HTMLDialogElement|null} modal Modal que será aberto.
     * @returns {void}
     */
    function openModal(modal) {
        if (!modal || typeof modal.showModal !== 'function') {
            return;
        }

        if (!modal.open) {
            modal.showModal();
        }
    }

    /**
     * Fecha um elemento dialog aberto.
     *
     * @param {HTMLDialogElement|null} modal Modal que será fechado.
     * @returns {void}
     */
    function closeModal(modal) {
        if (modal?.open) {
            modal.close();
        }
    }

    document.querySelectorAll('[data-app-modal]').forEach((modal) => {
        modal.querySelectorAll('[data-modal-close]').forEach((button) => {
            button.addEventListener('click', () => closeModal(modal));
        });

        // Clicar fora do conteúdo fecha somente modais que permitem essa ação.
        if (modal.hasAttribute('data-modal-close-backdrop')) {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    closeModal(modal);
                }
            });
        }

        if (modal.hasAttribute('data-modal-auto-open')) {
            openModal(modal);
        }

        if (modal.hasAttribute('data-modal-clean-url')) {
            const cleanUrl = new URL(window.location.href);
            cleanUrl.searchParams.delete('code');
            window.history.replaceState({}, document.title, cleanUrl);
        }
    });

    // Scripts de domínio usam esta API para manter a apresentação centralizada.
    window.OciPizzaModal = { open: openModal, close: closeModal };
})();
