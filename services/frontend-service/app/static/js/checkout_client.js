(() => {
    'use strict';

    const addressModal = document.querySelector(
        '[data-checkout-address-modal]'
    );

    if (!addressModal) {
        return;
    }

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
    addressModal.showModal();
    confirmationButton.addEventListener('click', redirectToProfile);

    // Impede fechar o aviso com Esc e permanecer em um checkout que não pode
    // ser concluído. A única ação disponível leva ao gerenciamento do perfil.
    addressModal.addEventListener('cancel', (event) => {
        event.preventDefault();
    });
})();
