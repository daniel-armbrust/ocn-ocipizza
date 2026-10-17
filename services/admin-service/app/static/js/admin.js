// Ponto de entrada dos scripts do painel administrativo.
// Cada módulo verifica a existência dos seus elementos antes de atuar,
// permitindo que todos os templates usem a mesma entrada com segurança.
import './common.js';
import './auth.js';
import './modals.js';
import './kitchen.js';
import './orders.js';
import './pizzas.js';
import './delivery.js';
import './users.js';
import './interaction_lock.js';
