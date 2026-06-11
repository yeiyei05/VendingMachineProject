// public/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('[Jidou-Tech] Interface initialisee.');

    // ── Actualisation automatique du dashboard toutes les 5 secondes ──
    const shell = document.getElementById('dashboard-live-data');
    if (!shell) return;

    const refreshUrl = shell.dataset.refreshUrl;
    if (!refreshUrl) return;

    function updateDashboard() {
        fetch(refreshUrl + '&ajax=1')
            .then(res => res.json())
            .then(data => {

                // Stock
                const stockValue = document.getElementById('stock-value');
                const stockFill  = document.getElementById('stock-fill');
                const stockMsg   = document.getElementById('stock-message');
                const stockStatus = document.getElementById('stock-status');
                const stockCard  = document.getElementById('stock-card');

                if (stockValue) {
                    const stock = parseInt(data.stock) || 0;
                    const isLow = stock <= 3;
                    const level = Math.max(0, Math.min(100, (stock / 5) * 100));

                    stockValue.textContent = stock;

                    if (stockFill)  stockFill.style.width = level + '%';
                    if (stockMsg)   stockMsg.textContent = isLow
                        ? 'Stock bas détecté. Planifier un remplissage du distributeur.'
                        : 'Niveau de stock stable, détecté par le capteur HC-SR04.';
                    if (stockStatus) {
                        stockStatus.textContent = isLow ? 'À recharger' : 'Opérationnel';
                        stockStatus.className = 'status-pill ' + (isLow ? 'is-low' : 'is-ready');
                    }
                    if (stockCard) {
                        stockCard.className = 'stock-panel ' + (isLow ? 'is-low' : 'is-ready');
                    }
                }

            })
            .catch(err => console.warn('[Dashboard] Erreur actualisation :', err));
    }

    // Lancer toutes les 5 secondes
    setInterval(updateDashboard, 5000);
});