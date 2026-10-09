(() => {
    'use strict';

    const profile = document.querySelector('[data-user-profile]');
    const updateProfileButton = profile?.querySelector('[data-update-profile]');
    const whatsappInput = profile?.querySelector('[data-profile-whatsapp]');

    if (!profile || !updateProfileButton || !whatsappInput) {
        return;
    }

    const updateWhatsappUrl = profile.dataset.updateWhatsappUrl;
    const csrfToken = profile.dataset.csrfToken;

    /**
     * Remove os caracteres utilizados somente pela máscara visual.
     *
     * @param {string} value Valor atual do campo.
     * @returns {string} Valor contendo somente dígitos.
     */
    function whatsappDigits(value) {
        return value.replace(/\D/g, '');
    }

    /**
     * Formata o WhatsApp apresentado na atualização do perfil.
     *
     * @param {string} value Valor atual do campo.
     * @returns {string} Número formatado para exibição.
     */
    function formatWhatsapp(value) {
        const digits = whatsappDigits(value);
        let formattedValue;

        if (digits.length === 0) {
            return '';
        }

        if (digits.length <= 2) {
            formattedValue = `(${digits}`;
        } else if (digits.length <= 7) {
            formattedValue = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
        } else {
            formattedValue = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
        }

        return whatsappInput.maxLength >= 0
            ? formattedValue.slice(0, whatsappInput.maxLength)
            : formattedValue;
    }

    /**
     * Obtém a mensagem retornada pelo BFF em uma resposta de erro.
     *
     * @param {Response} response Resposta HTTP recebida pelo navegador.
     * @returns {Promise<string>} Mensagem adequada para apresentação.
     */
    async function getResponseMessage(response) {
        try {
            const payload = await response.json();
            return payload?.data?.message
                || payload?.detail
                || 'Não foi possível atualizar o cadastro.';
        } catch (error) {
            return 'Não foi possível atualizar o cadastro.';
        }
    }

    /**
     * Envia o novo WhatsApp para a rota BFF responsável pelo perfil.
     *
     * @returns {Promise<void>}
     */
    async function updateProfile() {
        if (!whatsappInput.reportValidity()) {
            return;
        }

        updateProfileButton.disabled = true;
        updateProfileButton.setAttribute('aria-busy', 'true');
        window.OciPizzaInteractionLock.lock();

        try {
            const response = await window.fetch(updateWhatsappUrl, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    whatsapp: whatsappDigits(whatsappInput.value)
                })
            });

            if (response.redirected) {
                window.location.assign(response.url);
                return;
            }

            if (!response.ok) {
                throw new Error(await getResponseMessage(response));
            }

            window.OciPizza?.showToast(
                'Cadastro atualizado com sucesso.',
                'success'
            );
        } catch (error) {
            window.OciPizza?.showToast(
                error.message || 'Não foi possível atualizar o cadastro.',
                'error'
            );
        } finally {
            window.OciPizzaInteractionLock.unlock();
            updateProfileButton.disabled = false;
            updateProfileButton.removeAttribute('aria-busy');
        }
    }

    whatsappInput.value = formatWhatsapp(whatsappInput.value);
    whatsappInput.addEventListener('input', () => {
        whatsappInput.value = formatWhatsapp(whatsappInput.value);
    });
    updateProfileButton.addEventListener('click', updateProfile);
})();
