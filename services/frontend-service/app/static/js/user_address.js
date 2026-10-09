(() => {
    'use strict';

    const addressSelect = document.querySelector('[data-profile-address-select]');
    const addressPanels = document.querySelectorAll('[data-profile-address-panel]');
    const profile = document.querySelector('[data-user-profile]');

    if (!profile || !addressSelect || addressPanels.length === 0) {
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
     * Remove o endereço associado ao botão selecionado.
     *
     * @param {HTMLButtonElement} button Botão do endereço que será removido.
     * @returns {Promise<void>}
     */
    async function deleteAddress(button) {
        const confirmed = window.confirm(
            'Deseja realmente excluir este endereço?'
        );

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
                '/users/profile?code=USER_ADDRESS_SUCCESSFULLY_DELETED'
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

    addressSelect.addEventListener('change', renderSelectedAddress);
    addressPanels.forEach((panel) => {
        const deleteButton = panel.querySelector('[data-delete-address]');

        if (deleteButton?.dataset.addressId) {
            deleteButton.addEventListener('click', () => {
                deleteAddress(deleteButton);
            });
        }
    });
    renderSelectedAddress();
})();
