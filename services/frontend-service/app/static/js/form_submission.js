(() => {
    'use strict';

    const postForms = document.querySelectorAll('form[method="post" i]');

    /**
     * Bloqueia a interação com um formulário durante sua submissão.
     *
     * Os campos não recebem `disabled`, pois controles desabilitados deixam
     * de fazer parte do payload enviado pelo navegador.
     *
     * @param {HTMLFormElement} form Formulário que está sendo submetido.
     * @returns {void}
     */
    function lockForm(form) {
        form.dataset.submitting = 'true';
        form.setAttribute('aria-busy', 'true');
        form.inert = true;

        form.querySelectorAll('input, select, textarea, button').forEach((field) => {
            field.setAttribute('aria-disabled', 'true');

            if (
                (field instanceof HTMLInputElement && field.type !== 'hidden')
                || field instanceof HTMLTextAreaElement
            ) {
                field.readOnly = true;
            }
        });

        document.body.classList.add('is-submitting');
    }

    /**
     * Restaura formulários recuperados pelo cache de navegação do navegador.
     *
     * @returns {void}
     */
    function unlockForms() {
        postForms.forEach((form) => {
            delete form.dataset.submitting;
            form.removeAttribute('aria-busy');
            form.inert = false;

            form.querySelectorAll('[aria-disabled="true"]').forEach((field) => {
                field.removeAttribute('aria-disabled');

                if (
                    field instanceof HTMLInputElement
                    || field instanceof HTMLTextAreaElement
                ) {
                    field.readOnly = false;
                }
            });
        });

        document.body.classList.remove('is-submitting');
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

    window.addEventListener('pageshow', unlockForms);
})();
