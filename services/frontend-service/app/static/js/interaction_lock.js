(() => {
    'use strict';

    const postForms = document.querySelectorAll('form[method="post" i]');
    const lockedNavigationLinks = document.querySelectorAll(
        'a[data-lock-navigation]'
    );
    let activeLocks = 0;

    /**
     * Bloqueia a interação com toda a página enquanto uma operação aguarda
     * uma resposta do backend.
     *
     * @returns {void}
     */
    function lockScreen() {
        activeLocks += 1;
        document.body.classList.add('is-interaction-locked');
        document.body.setAttribute('aria-busy', 'true');
        document.body.inert = true;
    }

    /**
     * Libera a interação quando todas as operações pendentes terminarem.
     *
     * @returns {void}
     */
    function unlockScreen() {
        activeLocks = Math.max(0, activeLocks - 1);

        if (activeLocks > 0) {
            return;
        }

        document.body.classList.remove('is-interaction-locked');
        document.body.removeAttribute('aria-busy');
        document.body.inert = false;
    }

    /**
     * Bloqueia a página durante a submissão tradicional de um formulário.
     *
     * Os campos não recebem `disabled`, pois controles desabilitados deixam
     * de fazer parte do conteúdo enviado pelo navegador.
     *
     * @param {HTMLFormElement} form Formulário submetido.
     * @returns {void}
     */
    function lockForm(form) {
        form.dataset.submitting = 'true';
        lockScreen();
    }

    /**
     * Restaura o estado da página quando ela retorna do cache de navegação.
     *
     * @returns {void}
     */
    function resetLocks() {
        activeLocks = 0;
        postForms.forEach((form) => {
            delete form.dataset.submitting;
        });
        document.body.classList.remove('is-interaction-locked');
        document.body.removeAttribute('aria-busy');
        document.body.inert = false;
    }

    /**
     * Informa se o clique deve realizar uma navegação na aba atual.
     *
     * @param {MouseEvent} event Evento de clique recebido pelo link.
     * @param {HTMLAnchorElement} link Link que iniciou o evento.
     * @returns {boolean} `true` quando a navegação deve bloquear a página.
     */
    function shouldLockNavigation(event, link) {
        return (
            event.button === 0
            && !event.defaultPrevented
            && !event.ctrlKey
            && !event.metaKey
            && !event.shiftKey
            && !event.altKey
            && !link.hasAttribute('download')
            && (!link.target || link.target === '_self')
        );
    }

    postForms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (form.dataset.submitting === 'true') {
                event.preventDefault();
                return;
            }

            lockForm(form);
        });
    });

    lockedNavigationLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            if (shouldLockNavigation(event, link)) {
                lockScreen();
            }
        });
    });

    window.addEventListener('pageshow', resetLocks);

    window.OciPizzaInteractionLock = Object.freeze({
        lock: lockScreen,
        unlock: unlockScreen
    });
})();
