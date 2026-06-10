<div class="hero-landing">
    <h1 class="hero-title">Automated Retail Intelligence</h1>
    <p class="hero-subtitle">
        Découvrez la nouvelle génération de distributeurs connectés. Surveillance environnementale continue, interface utilisateur fluide et distribution robotique synchrone.
    </p>

    <div>
        <button class="btn-cyber" id="exploreBtn" style="padding: 15px 40px; font-size: 1.1rem;">
            Initialiser la console
        </button>
    </div>

    <div class="landing-footer">
        <span class="footer-link" onclick="openModal('modalCgu')">📜 Conditions d'Utilisation</span>
        <span class="footer-link" onclick="openModal('modalMentions')">⚖️ Mentions Légales</span>
    </div>
</div>

<script>
    // Le bouton central redirige l'utilisateur vers le dashboard d'administration de manière smooth
    document.getElementById('exploreBtn').addEventListener('click', () => {
        const dashboardLink = document.querySelector('[data-page="dashboard"]');
        if (dashboardLink) {
            dashboardLink.click();
        }
    });
</script>