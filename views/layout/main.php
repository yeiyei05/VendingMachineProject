<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vending Machine OS</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

<div class="app-container">
    <aside class="sidebar">
        <div class="sidebar-brand">
            VENDING<span>OS</span>
        </div>
        <ul class="sidebar-menu">
            <li><a href="index.php?page=home" class="menu-link <?php echo $page === 'home' ? 'active' : ''; ?>" data-page="home">🏠 Accueil</a></li>
            <li><a href="index.php?page=dashboard" class="menu-link <?php echo $page === 'dashboard' ? 'active' : ''; ?>" data-page="dashboard">📊 Dashboard</a></li>
            <li><a href="index.php?page=capteurs" class="menu-link <?php echo $page === 'capteurs' ? 'active' : ''; ?>" data-page="capteurs">🌡️ Capteurs & Actions</a></li>
            <li><a href="index.php?page=logout" class="logout-btn">🚪 Déconnexion</a></li>
        </ul>
    </aside>

    <div class="main-content">
        <header class="top-header">
            <div style="font-weight: 500; font-size: 1.1rem;">
                <span class="system-breadcrumb" id="systemBreadcrumb">Accueil</span> /
                <span id="current-page-title" style="color: var(--neon-blue); text-transform: uppercase; font-weight: bold;"><?php echo $page; ?></span>
            </div>

            <button class="theme-switch" id="themeToggle">
                <span id="themeIcon">🌙</span> <span id="themeText">Mode Sombre</span>
            </button>
        </header>

        <main id="app-viewport">
            <?php echo $content; ?>
        </main>
    </div>
</div>

<div class="modal-overlay" id="modalOverlay"></div>

<div class="cyber-modal" id="modalCgu">
    <h2 style="color: var(--neon-blue); margin-bottom: 15px;">Conditions Générales d'Utilisation</h2>
    <p style="line-height: 1.6; margin-bottom: 20px;">Ce système automatisé Vending OS est réservé aux opérateurs et ingénieurs de maintenance habilités. Les données de télémétrie collectées sont soumises aux protocoles de sécurité de l'entreprise...</p>
    <button class="btn-cyber" onclick="closeModals()">Fermer</button>
</div>

<div class="cyber-modal" id="modalMentions">
    <h2 style="color: var(--neon-purple); margin-bottom: 15px;">Mentions Légales</h2>
    <p style="line-height: 1.6; margin-bottom: 20px;">Éditeur du logiciel : Cyber-Retail Automation Systems Corp.<br>Hébergement : Serveur Local Décentralisé XAMPP v2026.<br>Conformité : Directive IoT et Sécurité Réseau.</p>
    <button class="btn-cyber" onclick="closeModals()">Fermer</button>
</div>

<script>
    // --- THÈME ---
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlEl.setAttribute('data-theme', savedTheme);
    updateToggleUI(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlEl.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlEl.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateToggleUI(newTheme);
    });

    function updateToggleUI(theme) {
        if (theme === 'dark') {
            themeIcon.innerText = '🌙'; themeText.innerText = 'Mode Sombre';
        } else {
            themeIcon.innerText = '☀️'; themeText.innerText = 'Mode Clair';
        }
    }

    // --- CLIC SUR ACCUEIL (BREADCRUMB) -> RENVOIE VERS LA LANDING PAGE ---
    document.getElementById('systemBreadcrumb').addEventListener('click', () => {
        const homeLink = document.querySelector('[data-page="home"]');
        if (homeLink) homeLink.click();
    });

    // --- INTERACTION MODALES SANS RECHARGEMENT ---
    function openModal(id) {
        document.getElementById('modalOverlay').classList.add('active');
        document.getElementById(id).classList.add('active');
    }

    function closeModals() {
        document.getElementById('modalOverlay').classList.remove('active');
        document.querySelectorAll('.cyber-modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }
    document.getElementById('modalOverlay').addEventListener('click', closeModals);

    // --- RAFRAICHISSEMENT DASHBOARD ---
    let dashboardRefreshTimer = null;
    let dashboardRefreshInProgress = false;

    function setMetricText(elementId, value, unit) {
        const element = document.getElementById(elementId);
        if (!element || value === undefined || value === null) return;
        element.textContent = `${value} ${unit}`;
    }

    function updateStockDisplay(stock) {
        const stockCard = document.getElementById('stock-card');
        const stockValue = document.getElementById('stock-value');
        if (!stockCard || !stockValue || stock === undefined || stock === null) return;

        const parsedStock = Number.parseInt(stock, 10);
        const stockIsLow = Number.isFinite(parsedStock) && parsedStock <= 3;
        const stockColor = stockIsLow ? '#ff4444' : 'var(--neon-green)';

        stockCard.style.borderLeftColor = stockColor;
        stockValue.style.color = stockColor;
        stockValue.style.textShadow = stockIsLow
            ? '0 0 8px rgba(255,68,68,0.4)'
            : '0 0 8px rgba(57,255,20,0.4)';

        const stockUnit = document.createElement('span');
        stockUnit.style.fontSize = '1.2rem';
        stockUnit.textContent = 'aliments';
        stockValue.replaceChildren(document.createTextNode(`${stock} `), stockUnit);

        const stockMessage = stockCard.querySelector('p:last-child');
        if (stockMessage) {
            stockMessage.style.color = stockIsLow ? '#ff4444' : 'var(--text-muted)';
            stockMessage.textContent = stockIsLow
                ? '\u26A0\uFE0F Stock bas - remplissage requis'
                : 'Niveau d\u00E9tect\u00E9 par HC-SR04.';
        }
    }

    function updateDashboardDisplay(data) {
        setMetricText('sensor-temp', data.temp, '\u00B0C');
        setMetricText('sensor-gaz', data.gaz, 'ppm');
        setMetricText('sensor-lux', data.lux, 'lx');
        updateStockDisplay(data.stock);
    }

    async function refreshDashboardData(container) {
        if (dashboardRefreshInProgress || !container.isConnected) return;

        dashboardRefreshInProgress = true;
        try {
            const separator = container.dataset.refreshUrl.includes('?') ? '&' : '?';
            const response = await fetch(`${container.dataset.refreshUrl}${separator}_=${Date.now()}`, {
                cache: 'no-store',
                headers: { 'Accept': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (container.isConnected) {
                updateDashboardDisplay(data);
            }
        } catch (error) {
            console.error('Erreur actualisation dashboard:', error);
        } finally {
            dashboardRefreshInProgress = false;
        }
    }

    function initDashboardAutoRefresh() {
        if (dashboardRefreshTimer) {
            clearInterval(dashboardRefreshTimer);
            dashboardRefreshTimer = null;
        }

        const dashboardContainer = document.getElementById('dashboard-live-data');
        if (!dashboardContainer) return;

        refreshDashboardData(dashboardContainer);
        dashboardRefreshTimer = setInterval(() => {
            refreshDashboardData(dashboardContainer);
        }, 1000);
    }

    // --- NAVIGATION SPA DYNAMIQUE ---
    document.querySelectorAll('.menu-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');
            const url = this.getAttribute('href');
            const viewport = document.getElementById('app-viewport');

            viewport.style.opacity = '0';
            viewport.style.transform = 'translateY(-10px)';

            setTimeout(() => {
                fetch(url + '&ajax=1')
                    .then(response => response.text())
                    .then(html => {
                        viewport.innerHTML = html;
                        document.getElementById('current-page-title').innerText = targetPage;
                        document.querySelectorAll('.menu-link').forEach(l => l.classList.remove('active'));
                        this.classList.add('active');
                        history.pushState(null, '', url);
                        viewport.style.opacity = '1';
                        viewport.style.transform = 'translateY(0)';
                        initDashboardAutoRefresh();
                    })
                    .catch(err => console.error('Erreur SPA:', err));
            }, 200);
        });
    });

    initDashboardAutoRefresh();

    window.addEventListener('popstate', () => { window.location.reload(); });
</script>
</body>
</html>
