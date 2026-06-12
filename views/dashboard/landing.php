<div class="landing-scroll-container">

    <div class="hero-landing-section">
        <div class="hero-content-box">
            <h1 class="hero-title">
                <span style="white-space: nowrap;">Distribution Automatique</span><br>
                Intelligente
            </h1>

            <p class="hero-subtitle">
                Découvrez la nouvelle génération de distributeurs connectés. Surveillance environnementale continue, interface utilisateur fluide et distribution robotique synchrone.
            </p>

            <div style="margin-top: 40px;">
                <button class="btn-cyber"
                        style="padding: 18px 50px; font-size: 1.1rem; border-radius: 30px;"
                        onclick="const link = document.querySelector('[data-page=\'dashboard\']'); link ? link.click() : window.location.href='index.php?page=dashboard';">
                    Initialiser la console
                </button>
            </div>
        </div>
    </div>

    <footer class="landing-corporate-footer">
        <div class="landing-footer-links">
            <span class="footer-link" onclick="openModal('modalCgu')">Conditions d'Utilisation</span>
            <span class="footer-link-separator">•</span>
            <span class="footer-link" onclick="openModal('modalMentions')">Mentions Légales</span>
        </div>
        <div class="landing-copyright">
            Copyright © 2026 VendoBot™. Tous droits réservés.
        </div>
    </footer>

</div>

<script>
    // Ce code fonctionne maintenant parfaitement car l'id "exploreBtn" existe sur le bouton !
    const exploreBtn = document.getElementById('exploreBtn');
    if (exploreBtn) {
        exploreBtn.addEventListener('click', () => {
            const dashboardLink = document.querySelector('[data-page="dashboard"]');
            if (dashboardLink) {
                dashboardLink.click(); // Tente une transition fluide si elle existe
            } else {
                window.location.href = "index.php?page=dashboard"; // Redirection classique sinon
            }
        });
    }
</script>