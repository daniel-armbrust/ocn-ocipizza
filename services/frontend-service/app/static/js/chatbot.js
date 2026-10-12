/*
 * Interação visual do assistente de atendimento.
 *
 * A integração com o backend será adicionada posteriormente. Por enquanto,
 * o componente oferece a experiência de abertura, sugestões e composição da
 * conversa sem realizar chamadas de rede.
 */
(function () {
    'use strict';

    const chatbot = document.querySelector('[data-chatbot]');

    if (!chatbot) {
        return;
    }

    // Mantém o widget preso à viewport, independentemente de estilos herdados
    // ou de regras de layout aplicadas ao conteúdo da página.
    const toggle = chatbot.querySelector('[data-chatbot-toggle]');
    const close = chatbot.querySelector('[data-chatbot-close]');
    const panel = chatbot.querySelector('[data-chatbot-panel]');
    const form = chatbot.querySelector('[data-chatbot-form]');
    const input = chatbot.querySelector('[data-chatbot-input]');
    const messages = chatbot.querySelector('[data-chatbot-messages]');
    const suggestions = chatbot.querySelector('[data-chatbot-suggestions]');

    /**
     * Abre ou fecha o painel do assistente.
     *
     * @param {boolean} isOpen Define se o painel deve ficar aberto.
     * @returns {void}
     */
    function setOpen(isOpen) {
        chatbot.classList.toggle('is-open', isOpen);
        toggle.setAttribute('aria-expanded', String(isOpen));
        panel.setAttribute('aria-hidden', String(!isOpen));
        panel.hidden = !isOpen;

        if (isOpen) {
            window.setTimeout(() => input?.focus(), 180);
        }
    }

    /**
     * Adiciona uma mensagem visual à conversa.
     *
     * @param {string} text Texto exibido no balão.
     * @param {'assistant'|'user'} author Origem da mensagem.
     * @returns {void}
     */
    function appendMessage(text, author) {
        const message = document.createElement('div');
        message.className = `chatbot-message chatbot-message-${author}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }

    /**
     * Processa uma mensagem localmente enquanto a API do chatbot não existe.
     *
     * @param {string} text Texto enviado pelo visitante.
     * @returns {void}
     */
    function submitMessage(text) {
        const normalizedText = text.trim();

        if (!normalizedText) {
            return;
        }

        appendMessage(normalizedText, 'user');
        input.value = '';
        suggestions.hidden = true;
        window.setTimeout(() => {
            appendMessage(
                'Em breve poderei ajudar você por aqui. Enquanto isso, confira nosso cardápio! 🍕',
                'assistant'
            );
        }, 350);
    }

    toggle.addEventListener('click', () => {
        setOpen(!chatbot.classList.contains('is-open'));
    });

    close.addEventListener('click', () => setOpen(false));

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        submitMessage(input.value);
    });

    chatbot.querySelectorAll('[data-chatbot-suggestion]').forEach((button) => {
        button.addEventListener('click', () => submitMessage(button.dataset.chatbotSuggestion));
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && chatbot.classList.contains('is-open')) {
            setOpen(false);
        }
    });
})();
