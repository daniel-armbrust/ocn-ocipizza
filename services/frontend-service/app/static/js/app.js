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
    const orderStorageKey = 'ocipizza.orderCount';

    function readOrderCount() {
        const storedCount = Number.parseInt(
            window.localStorage.getItem(orderStorageKey) || '0',
            10
        );

        return Number.isSafeInteger(storedCount) && storedCount > 0
            ? storedCount
            : 0;
    }

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

    function addPizzaToOrder() {
        const count = readOrderCount() + 1;
        window.localStorage.setItem(orderStorageKey, String(count));
        renderOrderCount(count);
        return count;
    }

    renderOrderCount(readOrderCount());

    window.OciPizza = Object.freeze({
        addPizzaToOrder,
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
