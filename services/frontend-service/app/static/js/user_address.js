(() => {
    'use strict';

    const zipCodeFields = document.querySelectorAll('[data-zip-code-mask]');
    const numericFields = document.querySelectorAll('[data-numeric-only]');
    const addressSelect = document.querySelector('[data-profile-address-select]');
    const addressPanels = document.querySelectorAll('[data-profile-address-panel]');
    const deleteAddressButtons = document.querySelectorAll(
        '[data-delete-address]'
    );
    const profile = document.querySelector('[data-user-profile]');
    const deletionModal = document.querySelector('[data-address-delete-modal]');
    const confirmDeletionButton = document.querySelector(
        '[data-confirm-address-deletion]'
    );
    const cancelDeletionButton = document.querySelector(
        '[data-cancel-address-deletion]'
    );

    /**
     * Formata um CEP no padrão 99999-999.
     *
     * @param {string} value Valor atual do campo de CEP.
     * @returns {string} CEP contendo somente oito dígitos e o hífen.
     */
    function formatZipCode(value) {
        const digits = value.replace(/\D/g, '').slice(0, 8);

        if (digits.length <= 5) {
            return digits;
        }

        return `${digits.slice(0, 5)}-${digits.slice(5)}`;
    }

    zipCodeFields.forEach((field) => {
        field.value = formatZipCode(field.value);
        field.addEventListener('input', () => {
            field.value = formatZipCode(field.value);
        });
    });

    // Remove imediatamente caracteres não numéricos dos campos que aceitam
    // exclusivamente dígitos, inclusive quando o conteúdo for colado.
    numericFields.forEach((field) => {
        field.value = field.value.replace(/\D/g, '');
        field.addEventListener('input', () => {
            field.value = field.value.replace(/\D/g, '');
        });
    });

    if (!profile) {
        return;
    }

    const csrfToken = profile.dataset.csrfToken;

    /**
     * Exibe os campos correspondentes ao endereço selecionado.
     *
     * @returns {void}
     */
    function renderSelectedAddress() {
        addressPanels.forEach((panel) => {
            panel.hidden = panel.dataset.profileAddressPanel !== addressSelect.value;
        });
    }

    /**
     * Solicita a confirmação da exclusão por meio do modal da aplicação.
     *
     * @returns {Promise<boolean>} `true` quando o usuário confirma a
     *     exclusão; caso contrário, `false`.
     */
    function confirmAddressDeletion() {
        if (
            !deletionModal
            || !confirmDeletionButton
            || !cancelDeletionButton
        ) {
            return Promise.resolve(false);
        }

        return new Promise((resolve) => {
            let resolved = false;

            /**
             * Encerra o modal e entrega a decisão tomada pelo usuário.
             *
             * @param {boolean} confirmed Indica se a exclusão foi confirmada.
             * @returns {void}
             */
            function finish(confirmed) {
                if (resolved) {
                    return;
                }

                resolved = true;
                confirmDeletionButton.removeEventListener('click', confirm);
                cancelDeletionButton.removeEventListener('click', cancel);
                deletionModal.removeEventListener('cancel', cancel);

                window.OciPizzaModal?.close(deletionModal);

                resolve(confirmed);
            }

            /**
             * Confirma a exclusão solicitada.
             *
             * @returns {void}
             */
            function confirm() {
                finish(true);
            }

            /**
             * Cancela a exclusão solicitada.
             *
             * @param {Event} event Evento opcional de cancelamento do dialog.
             * @returns {void}
             */
            function cancel(event) {
                event?.preventDefault();
                finish(false);
            }

            confirmDeletionButton.addEventListener('click', confirm);
            cancelDeletionButton.addEventListener('click', cancel);
            deletionModal.addEventListener('cancel', cancel);
            window.OciPizzaModal?.open(deletionModal);
        });
    }

    /**
     * Remove o endereço associado ao botão selecionado.
     *
     * @param {HTMLButtonElement} button Botão do endereço que será removido.
     * @returns {Promise<void>}
     */
    async function deleteAddress(button) {
        const confirmed = await confirmAddressDeletion();

        if (!confirmed) {
            return;
        }

        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        window.OciPizzaInteractionLock.lock();

        try {
            const response = await window.fetch(
                button.dataset.deleteAddressUrl,
                {
                    method: 'DELETE',
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'text/html',
                        'X-CSRFToken': csrfToken
                    }
                }
            );

            if (response.redirected) {
                window.location.assign(response.url);
                return;
            }

            if (!response.ok) {
                throw new Error('Não foi possível remover o endereço.');
            }

            window.location.assign(
                '/users/profile/addresses'
                + '?code=USER_ADDRESS_SUCCESSFULLY_DELETED'
            );
        } catch (error) {
            window.OciPizza?.showToast(
                error.message || 'Não foi possível remover o endereço.',
                'error'
            );
        } finally {
            window.OciPizzaInteractionLock.unlock();
            button.disabled = false;
            button.removeAttribute('aria-busy');
        }
    }

    if (addressSelect && addressPanels.length > 0) {
        addressSelect.addEventListener('change', renderSelectedAddress);
        renderSelectedAddress();
    }

    // Os cards do painel não dependem mais de um seletor para exibir os
    // endereços; cada botão é associado diretamente ao seu próprio recurso.
    deleteAddressButtons.forEach((deleteButton) => {
        if (deleteButton.dataset.addressId) {
            deleteButton.addEventListener('click', () => {
                deleteAddress(deleteButton);
            });
        }
    });
})();
