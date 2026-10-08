(() => {
    'use strict';

    const cart = document.querySelector('[data-cart]');

    if (!cart || !window.OciPizza) {
        return;
    }

    const emptyState = cart.querySelector('[data-cart-empty]');
    const cartContent = cart.querySelector('[data-cart-content]');
    const itemsContainer = cart.querySelector('[data-cart-items]');
    const itemTemplate = cart.querySelector('[data-cart-item-template]');
    const totalQuantity = cart.querySelector('[data-cart-total-quantity]');
    const total = cart.querySelector('[data-cart-total]');
    const clearCartButton = cart.querySelector('[data-clear-cart]');
    const fallbackImage = cart.dataset.fallbackImage;
    const currencyFormatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });

    /**
     * Formata um valor numérico como moeda brasileira.
     *
     * @param {number} value Valor monetário a ser formatado.
     * @returns {string} Valor formatado em reais.
     */
    function formatCurrency(value) {
        return currencyFormatter.format(value);
    }

    /**
     * Cria o elemento visual correspondente a um item do carrinho.
     *
     * @param {object} item Item recuperado do localStorage.
     * @returns {DocumentFragment} Fragmento pronto para ser renderizado.
     */
    function createCartItem(item) {
        const fragment = itemTemplate.content.cloneNode(true);
        const image = fragment.querySelector('[data-cart-item-image]');
        const name = fragment.querySelector('[data-cart-item-name]');
        const unitPrice = fragment.querySelector('[data-cart-item-unit-price]');
        const quantity = fragment.querySelector('[data-cart-item-quantity]');
        const subtotal = fragment.querySelector('[data-cart-item-subtotal]');
        const decreaseButton = fragment.querySelector('[data-decrease-quantity]');
        const increaseButton = fragment.querySelector('[data-increase-quantity]');
        const removeButton = fragment.querySelector('[data-remove-cart-item]');

        image.src = item.imageUrl || fallbackImage;
        image.alt = `Pizza ${item.name}`;
        image.addEventListener('error', () => {
            image.src = fallbackImage;
        }, { once: true });
        name.textContent = item.name;
        unitPrice.textContent = `${formatCurrency(Number(item.price))} por unidade`;
        quantity.textContent = String(item.quantity);
        subtotal.textContent = formatCurrency(Number(item.price) * item.quantity);
        decreaseButton.disabled = item.quantity <= 1;

        decreaseButton.addEventListener('click', () => {
            window.OciPizza.updateCartItemQuantity(item.id, item.quantity - 1);
        });
        increaseButton.addEventListener('click', () => {
            window.OciPizza.updateCartItemQuantity(item.id, item.quantity + 1);
        });
        removeButton.addEventListener('click', () => {
            window.OciPizza.updateCartItemQuantity(item.id, 0);
        });

        return fragment;
    }

    /**
     * Renderiza itens, quantidades e total do carrinho.
     *
     * @returns {void}
     */
    function renderCart() {
        const items = window.OciPizza.readCart();
        const isEmpty = items.length === 0;

        emptyState.hidden = !isEmpty;
        cartContent.hidden = isEmpty;
        itemsContainer.replaceChildren();

        if (isEmpty) {
            return;
        }

        let quantitySum = 0;
        let totalValue = 0;

        items.forEach((item) => {
            quantitySum += item.quantity;
            totalValue += Number(item.price) * item.quantity;
            itemsContainer.appendChild(createCartItem(item));
        });

        totalQuantity.textContent = String(quantitySum);
        total.textContent = formatCurrency(totalValue);
    }

    clearCartButton.addEventListener('click', () => {
        window.OciPizza.clearCart();
    });
    window.addEventListener('ocipizza:cart-updated', renderCart);
    renderCart();
})();
