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
            <li><a href="index.php?page=dashboard" class="menu-link <?php echo $page === 'dashboard' ? 'active' : ''; ?>" data-page="dashboard">📊 Accueil</a></li>
            <li><a href="index.php?page=capteurs" class="menu-link <?php echo $page === 'capteurs' ? 'active' : ''; ?>" data-page="capteurs">🌡️ Capteurs & Actions</a></li>
            <li><a href="index.php?page=logout" class="logout-btn">🚪 Déconnexion</a></li>
        </ul>
    </aside>

    <div class="main-content">
        <header class="top-header">
            <div style="font-weight: 500; font-size: 1.1rem;">
                Système / <span id="current-page-title" style="color: var(--neon-blue); text-transform: uppercase; font-weight: bold;"><?php echo $page; ?></span>
            </div>

            <button class="theme-switch" id="themeToggle">
                <span id="themeIcon">🌙</span> <span id="themeText">Mode Sombre</span>
            </button>
        </header>

        <main id="app-viewport">
            <?php echo $content; ?>
        </main>
        </main>
    </div>

    <script>
        // --- GESTION DU THEME CLAIR / SOMBRE ---
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
                themeIcon.innerText = '🌙';
                themeText.innerText = 'Mode Sombre';
            } else {
                themeIcon.innerText = '☀️';
                themeText.innerText = 'Mode Clair';
            }
        }

        // --- NAVIGATION DYNAMIQUE SANS RECHARGEMENT (AJAX / FETCH) ---
        document.querySelectorAll('.menu-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Bloque le rechargement brutal

                const targetPage = this.getAttribute('data-page');
                const url = this.getAttribute('href');

                // Petite animation de sortie sur le viewport
                const viewport = document.getElementById('app-viewport');
                viewport.style.opacity = '0';
                viewport.style.transform = 'translateY(-10px)';

                setTimeout(() => {
                    // Fetch va chercher le contenu de la page en tâche de fond
                    fetch(url + '&ajax=1')
                        .then(response => response.text())
                        .then(html => {
                            viewport.innerHTML = html;
                            document.getElementById('current-page-title').innerText = targetPage;

                            // Met à jour la classe active sur le menu
                            document.querySelectorAll('.menu-link').forEach(l => l.classList.remove('active'));
                            this.classList.add('active');

                            // Remet l'historique de navigation à jour dans le navigateur
                            history.pushState(null, '', url);

                            // Animation d'entrée super smooth
                            viewport.style.opacity = '1';
                            viewport.style.transform = 'translateY(0)';
                        })
                        .catch(err => console.error('Erreur de chargement SPA:', err));
                }, 200);
            });
        });

        // Gérer le bouton "Précédent" du navigateur
        window.addEventListener('popstate', () => {
            window.location.reload();
        });
    </script>
</body>
</html>