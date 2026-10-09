(() => {
    'use strict';

    const catalog = document.querySelector('[data-pizza-catalog]');

    if (!catalog) {
        return;
    }

    const fallbackImage = catalog.dataset.fallbackImage;
    const clearFiltersButton = catalog.querySelector('[data-clear-filters]');
    const currentUrl = new URL(window.location.href);

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
            window.OciPizza?.showToast(
                `${pizzaName} adicionada à sua escolha.`,
                'success'
            );
        });
    });

    clearFiltersButton?.addEventListener('click', () => {
        window.location.assign('/pizzas');
    });

    if (
        currentUrl.search.length > 0
    ) {
        catalog.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

})();
