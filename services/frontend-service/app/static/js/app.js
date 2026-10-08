(() => {
    'use strict';

    const navToggle = document.querySelector('[data-nav-toggle]');
    const navigation = document.querySelector('[data-nav]');

    if (navToggle && navigation) {
        navToggle.addEventListener('click', () => {
            const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', String(!isOpen));
            navigation.classList.toggle('is-open', !isOpen);
        });

        navigation.addEventListener('click', (event) => {
            if (event.target.closest('a')) {
                navToggle.setAttribute('aria-expanded', 'false');
                navigation.classList.remove('is-open');
            }
        });
    }

    document.querySelectorAll('[data-current-year]').forEach((element) => {
        element.textContent = String(new Date().getFullYear());
    });

    const toastRegion = document.querySelector('[data-toast-region]');
    const orderIndicator = document.querySelector('[data-order-indicator]');
    const orderCount = document.querySelector('[data-order-count]');
    const cartStorageKey = 'ocipizza.cart';

    /**
     * Recupera e normaliza os itens armazenados no carrinho.
     *
     * @returns {Array<object>} Itens válidos armazenados no navegador.
     */
    function readCart() {
        try {
            const storedCart = JSON.parse(
                window.localStorage.getItem(cartStorageKey) || '[]'
            );

            if (!Array.isArray(storedCart)) {
                return [];
            }

            return storedCart.filter((item) => (
                item
                && typeof item.id === 'string'
                && typeof item.name === 'string'
                && Number.isFinite(Number(item.price))
                && Number.isSafeInteger(item.quantity)
                && item.quantity > 0
            ));
        } catch (error) {
            window.localStorage.removeItem(cartStorageKey);
            return [];
        }
    }

    /**
     * Persiste os itens e notifica os componentes da página.
     *
     * @param {Array<object>} items Itens atualizados do carrinho.
     * @returns {void}
     */
    function writeCart(items) {
        window.localStorage.setItem(cartStorageKey, JSON.stringify(items));
        window.dispatchEvent(new CustomEvent('ocipizza:cart-updated'));
    }

    /**
     * Calcula a quantidade total de pizzas do carrinho.
     *
     * @param {Array<object>} items Itens utilizados no cálculo.
     * @returns {number} Soma das quantidades dos itens.
     */
    function cartItemCount(items) {
        return items.reduce((total, item) => total + item.quantity, 0);
    }

    /**
     * Atualiza o contador exibido no menu superior.
     *
     * @param {number} count Quantidade total de pizzas.
     * @returns {void}
     */
    function renderOrderCount(count) {
        if (!orderCount || !orderIndicator) {
            return;
        }

        orderCount.textContent = String(count);
        orderIndicator.setAttribute(
            'aria-label',
            `Pedido com ${count} ${count === 1 ? 'pizza' : 'pizzas'}`
        );
    }

    /**
     * Adiciona uma pizza ao carrinho ou incrementa sua quantidade.
     *
     * @param {object} pizza Dados públicos da pizza selecionada.
     * @returns {number} Quantidade total após a inclusão.
     */
    function addPizzaToOrder(pizza) {
        const items = readCart();
        const existingItem = items.find((item) => item.id === pizza.id);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            items.push({
                id: pizza.id,
                name: pizza.name,
                price: Number(pizza.price),
                imageUrl: pizza.imageUrl,
                quantity: 1
            });
        }

        writeCart(items);
        return cartItemCount(items);
    }

    /**
     * Altera a quantidade de uma pizza ou a remove quando chegar a zero.
     *
     * @param {string} pizzaId Identificador da pizza.
     * @param {number} quantity Nova quantidade desejada.
     * @returns {void}
     */
    function updateCartItemQuantity(pizzaId, quantity) {
        const items = readCart();
        const item = items.find((cartItem) => cartItem.id === pizzaId);

        if (!item) {
            return;
        }

        item.quantity = quantity;
        writeCart(items.filter((cartItem) => cartItem.quantity > 0));
    }

    /**
     * Remove todos os itens armazenados no carrinho.
     *
     * @returns {void}
     */
    function clearCart() {
        writeCart([]);
    }

    // Remove o contador legado, que não possuía dados das pizzas.
    window.localStorage.removeItem('ocipizza.orderCount');
    renderOrderCount(cartItemCount(readCart()));
    window.addEventListener('ocipizza:cart-updated', () => {
        renderOrderCount(cartItemCount(readCart()));
    });

    window.OciPizza = Object.freeze({
        addPizzaToOrder,
        clearCart,
        readCart,
        updateCartItemQuantity,
        showToast(message, type = 'info') {
            if (!toastRegion || !message) {
                return;
            }

            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            toastRegion.appendChild(toast);

            window.setTimeout(() => {
                toast.classList.add('is-leaving');
                toast.addEventListener('animationend', () => toast.remove(), { once: true });
            }, 4000);
        }
    });
})();
