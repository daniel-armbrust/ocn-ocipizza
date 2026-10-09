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
    const checkoutButton = cart.querySelector('[data-cart-checkout]');
    const fallbackImage = cart.dataset.fallbackImage;
    const checkoutUrl = cart.dataset.checkoutUrl;
    const csrfToken = cart.dataset.csrfToken;
    let checkoutInProgress = false;
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

    /**
     * Converte os itens internos do carrinho no contrato do checkout.
     *
     * @param {Array<object>} items Itens recuperados do localStorage.
     * @returns {{items: Array<{pizza_id: string, quantity: number}>}} Payload
     *     enviado ao backend.
     */
    function createCheckoutPayload(items) {
        return {
            items: items.map((item) => ({
                pizza_id: item.id,
                quantity: item.quantity
            }))
        };
    }

    /**
     * Obtém uma mensagem legível de uma resposta de falha do checkout.
     *
     * @param {Response} response Resposta HTTP retornada pelo backend.
     * @returns {Promise<string>} Mensagem que será apresentada ao usuário.
     */
    async function getCheckoutErrorMessage(response) {
        try {
            const payload = await response.json();
            return payload?.data?.message
                || payload?.detail
                || 'Não foi possível finalizar o pedido.';
        } catch (error) {
            return 'Não foi possível finalizar o pedido.';
        }
    }

    /**
     * Envia as pizzas armazenadas no navegador para o checkout do BFF.
     *
     * @returns {Promise<void>}
     */
    async function submitCheckout() {
        const items = window.OciPizza.readCart();

        if (items.length === 0 || checkoutInProgress) {
            return;
        }

        checkoutInProgress = true;
        checkoutButton.setAttribute('aria-busy', 'true');
        checkoutButton.textContent = 'Finalizando...';
        window.OciPizzaInteractionLock.lock();

        try {
            const response = await window.fetch(checkoutUrl, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(createCheckoutPayload(items))
            });

            if (!response.ok) {
                throw new Error(await getCheckoutErrorMessage(response));
            }

            if (response.redirected) {
                window.location.assign(response.url);
                return;
            }

            window.OciPizza.showToast(
                'Pedido enviado com sucesso.',
                'success'
            );
        } catch (error) {
            window.OciPizza.showToast(
                error.message || 'Não foi possível finalizar o pedido.',
                'error'
            );
        } finally {
            window.OciPizzaInteractionLock.unlock();
            checkoutInProgress = false;
            checkoutButton.removeAttribute('aria-busy');
            checkoutButton.textContent = 'Finalizar Pedido';
            renderCart();
        }
    }

    clearCartButton.addEventListener('click', () => {
        window.OciPizza.clearCart();
    });
    checkoutButton.addEventListener('click', submitCheckout);
    window.addEventListener('ocipizza:cart-updated', renderCart);
    renderCart();
})();
