<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VendoBot OS</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

<div class="app-container">
    <aside class="sidebar">
        <div class="sidebar-brand">VENDO<span>BOT</span></div>
        <ul class="sidebar-menu">
            <li><a href="index.php?page=home" class="menu-link <?php echo $page === 'home' ? 'active' : ''; ?>" data-page="home">Accueil</a></li>
            <li><a href="index.php?page=dashboard" class="menu-link <?php echo $page === 'dashboard' ? 'active' : ''; ?>" data-page="dashboard">Dashboard</a></li>
            <li><a href="index.php?page=capteurs" class="menu-link <?php echo $page === 'capteurs' ? 'active' : ''; ?>" data-page="capteurs">Capteurs & Actionneurs</a></li>
            <li><a href="index.php?page=logout" class="logout-btn">Déconnexion</a></li>
        </ul>
    </aside>

    <div class="main-content">
        <header class="top-header">
            <div style="font-weight: 500; font-size: 1.1rem;">
                <span class="system-breadcrumb" id="systemBreadcrumb">Accueil</span> /
                <span id="current-page-title" style="color: var(--neon-blue); text-transform: uppercase; font-weight: bold;"><?php echo $page; ?></span>
            </div>
            <button class="theme-switch" id="themeToggle">
                <span id="themeText">Mode Sombre</span>
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
    <p style="line-height: 1.6; margin-bottom: 20px; color: var(--text-color);">Ce système automatisé VendoBot est réservé aux opérateurs et ingénieurs de maintenance habilités. Les données de télémétrie collectées sont soumises aux protocoles de sécurité de l'entreprise.</p>
    <button class="btn-cyber" onclick="closeModals()">Fermer</button>
</div>
<div class="cyber-modal" id="modalMentions">
    <h2 style="color: var(--neon-purple); margin-bottom: 15px;">Mentions Légales</h2>
    <p style="line-height: 1.6; margin-bottom: 20px; color: var(--text-color);">Éditeur du logiciel : Automation Systems Corp.<br>Hébergement : Serveur Local Décentralisé XAMPP v2026.<br>Conformité : Directive IoT et Sécurité Réseau.</p>
    <button class="btn-cyber" onclick="closeModals()">Fermer</button>
</div>

<script>
    // --- PERMUTATEUR DE THEME (VERSION INCASSABLE) ---
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlEl.setAttribute('data-theme', savedTheme);
    updateToggleUI(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = htmlEl.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleUI(newTheme);
        });
    }

    // Sécurité défensive : s'adapte à la structure HTML exacte pour appliquer le texte
    function updateToggleUI(theme) {
        const themeText = document.getElementById('themeText');
        const textValue = (theme === 'dark') ? 'Mode Sombre' : 'Mode Clair';

        if (themeText) {
            themeText.innerText = textValue;
        } else if (themeToggle) {
            themeToggle.innerText = textValue;
        }
    }

    // --- GESTION DES MODALES CORPORATE ---
    function openModal(id) {
        document.getElementById('modalOverlay').classList.add('active');
        document.getElementById(id).classList.add('active');
    }
    function closeModals() {
        document.getElementById('modalOverlay').classList.remove('active');
        document.querySelectorAll('.cyber-modal').forEach(m => m.classList.remove('active'));
    }
    document.getElementById('modalOverlay').addEventListener('click', closeModals);

    // --- FIL D'ARIANE ---
    document.getElementById('systemBreadcrumb').addEventListener('click', () => {
        const homeLink = document.querySelector('[data-page="home"]');
        if (homeLink) homeLink.click();
    });

    // --- NAV DYNAMIQUE (SPA ENGINE) ---
    document.querySelectorAll('.menu-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');
            const url = this.getAttribute('href');
            const viewport = document.getElementById('app-viewport');

            viewport.style.opacity = '0';
            setTimeout(() => {
                fetch(url + '&ajax=1')
                    .then(r => r.text())
                    .then(html => {
                        viewport.innerHTML = html;
                        document.getElementById('current-page-title').innerText = targetPage;
                        document.querySelectorAll('.menu-link').forEach(l => l.classList.remove('active'));
                        this.classList.add('active');
                        history.pushState(null, '', url);
                        viewport.style.opacity = '1';
                    });
            }, 150);
        });
    });
    window.addEventListener('popstate', () => window.location.reload());
</script>
</body>
</html>