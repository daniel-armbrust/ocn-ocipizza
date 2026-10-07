(() => {
    'use strict';

    const catalog = document.querySelector('[data-pizza-catalog]');

    if (!catalog) {
        return;
    }

    const fallbackImage = catalog.dataset.fallbackImage;
    const clearFiltersButton = catalog.querySelector('[data-clear-filters]');
    const currentUrl = new URL(window.location.href);
    const authenticationSucceeded = (
        currentUrl.searchParams.get('code') === 'USER_AUTHENTICATION_SUCCESS'
        || document.querySelector('[data-authentication-success]') !== null
    );

    if (authenticationSucceeded) {
        const scrollToPageTop = () => {
            const previousScrollBehavior = document.documentElement.style.scrollBehavior;
            document.documentElement.style.scrollBehavior = 'auto';
            window.scrollTo(0, 0);
            document.documentElement.style.scrollBehavior = previousScrollBehavior;
        };

        // Impede que o navegador restaure a posição anterior durante o
        // redirecionamento realizado após a autenticação.
        if ('scrollRestoration' in window.history) {
            window.history.scrollRestoration = 'manual';
        }

        // A mensagem já foi renderizada pelo backend. Remove somente o
        // código para impedir que ela reapareça ao atualizar a página.
        currentUrl.searchParams.delete('code');
        window.history.replaceState({}, '', currentUrl);

        // O retorno do login deve sempre apresentar o início da página,
        // onde a mensagem de autenticação foi renderizada.
        scrollToPageTop();
        window.requestAnimationFrame(scrollToPageTop);
        window.addEventListener('pageshow', scrollToPageTop, { once: true });
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
            window.OciPizza?.addPizzaToOrder();
            window.OciPizza?.showToast(
                `${pizzaName} adicionada à sua escolha.`,
                'success'
            );
        });
    });

    clearFiltersButton?.addEventListener('click', () => {
        window.location.assign('/pizzas');
    });

})();
