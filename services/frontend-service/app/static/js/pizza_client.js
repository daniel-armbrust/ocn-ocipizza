(() => {
    'use strict';

    const catalog = document.querySelector('[data-pizza-catalog]');

    if (!catalog) {
        return;
    }

    const fallbackImage = catalog.dataset.fallbackImage;
    const clearFiltersButton = catalog.querySelector('[data-clear-filters]');
    const pizzaAddedModal = document.querySelector('[data-pizza-added-modal]');
    const pizzaAddedMessage = document.querySelector('[data-pizza-added-message]');
    const currentUrl = new URL(window.location.href);
    const orderSucceeded = (
        currentUrl.searchParams.get('code') === 'CART_ORDER_SUCCESSFULLY_CREATED'
        || document.querySelector('[data-order-success]') !== null
    );
    let pizzaAddedModalTimeout;

    // A limpeza do carrinho é uma responsabilidade global de app.js. Aqui, a
    // página apenas remove o código da URL e mantém o topo e a mensagem de
    // confirmação visíveis após o redirecionamento.
    if (orderSucceeded) {
        currentUrl.searchParams.delete('code');
        window.history.replaceState({}, '', currentUrl);
        window.scrollTo(0, 0);
    }

    /**
     * Exibe temporariamente a confirmação de inclusão da pizza no carrinho.
     *
     * @param {string} pizzaName Nome da pizza adicionada.
     * @returns {void}
     */
    function showPizzaAddedModal(pizzaName) {
        if (!pizzaAddedModal || !pizzaAddedMessage) {
            return;
        }

        window.clearTimeout(pizzaAddedModalTimeout);
        pizzaAddedMessage.textContent = (
            `${pizzaName} foi adicionada ao seu carrinho.`
        );

        if (!pizzaAddedModal.open) {
            pizzaAddedModal.showModal();
        }

        pizzaAddedModalTimeout = window.setTimeout(() => {
            if (pizzaAddedModal.open) {
                pizzaAddedModal.close();
            }
        }, 3000);
    }

    catalog.querySelectorAll('[data-pizza-image]').forEach((image) => {
        image.addEventListener('error', () => {
            image.src = fallbackImage;
            image.classList.add('is-fallback');
        }, { once: true });
    });

    catalog.querySelectorAll('[data-add-pizza]').forEach((button) => {
        button.addEventListener('click', () => {
            const pizzaName = button.dataset.pizzaName || 'Pizza';
            window.OciPizza?.addPizzaToOrder({
                id: button.dataset.pizzaId,
                name: pizzaName,
                price: Number(button.dataset.pizzaPrice),
                imageUrl: button.dataset.pizzaImageUrl
            });
            showPizzaAddedModal(pizzaName);
        });
    });

    clearFiltersButton?.addEventListener('click', () => {
        window.location.assign('/pizzas');
    });

    if (currentUrl.search.length > 0 && !orderSucceeded) {
        catalog.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

})();
