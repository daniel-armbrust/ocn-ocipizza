//
// js/interaction_lock.js
//

(() => {
    'use strict';

    // Formulários POST aguardam uma resposta do backend antes de permitir
    // outra interação ou uma segunda submissão.
    const postForms = document.querySelectorAll('form[method="post" i]');
    const lockedNavigationLinks = document.querySelectorAll(
        'a[data-lock-navigation]'
    );
    let activeLocks = 0;

    /**
     * Bloqueia a interface enquanto uma operação aguarda resposta.
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
     * Libera a interface quando todas as operações pendentes terminarem.
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
     * Bloqueia a interface durante uma submissão tradicional.
     *
     * Os campos não são desabilitados, pois controles desabilitados deixam de
     * fazer parte dos dados enviados pelo navegador.
     *
     * @param {HTMLFormElement} form Formulário submetido.
     * @returns {void}
     */
    function lockForm(form) {
        form.dataset.submitting = 'true';
        lockScreen();
    }

    /**
     * Restaura o estado quando a página retorna do cache de navegação.
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
     * Determina se um link representa uma navegação na aba atual.
     *
     * @param {MouseEvent} event Evento de clique recebido pelo link.
     * @param {HTMLAnchorElement} link Link que iniciou o evento.
     * @returns {boolean} `true` quando a navegação deve ser bloqueada.
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
            // A validação ou um modal pode cancelar o envio antes deste
            // listener; nesse caso, não existe requisição aguardando resposta.
            if (event.defaultPrevented) {
                return;
            }

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

    window.AdminInteractionLock = Object.freeze({
        lock: lockScreen,
        unlock: unlockScreen
    });
})();
