// public/js/main.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("🌐 [Jidou-Tech] Système d'interface Cyberpunk initialisé.");

    // 1. Simulation d'évolution des capteurs en temps réel (en attendant la BDD complète)
    // Cela évite d'avoir un site figé lors de la démonstration devant le jury !
    setInterval(() => {
        // Simulation d'une légère variation de température (-0.1°C ou +0.1°C)
        const tempElement = document.querySelector('.cyber-card:nth-child(1) p');
        if (tempElement) {
            let currentTemp = parseFloat(tempElement.textContent);
            let variation = (Math.random() * 0.4 - 0.2).toFixed(1);
            let newTemp = (currentTemp + parseFloat(variation)).toFixed(1);
            // On s'assure de rester dans des normes de distributeur frais (entre 3°C et 6°C)
            if (newTemp > 2 && newTemp < 7) {
                tempElement.innerHTML = `${newTemp} <span style="font-size: 1.5rem; color: var(--text-muted);">°C</span>`;
            }
        }

        // Simulation d'une légère variation du taux de gaz
        const gazElement = document.querySelector('.cyber-card:nth-color(2) p, .cyber-card[style*="var(--neon-green)"] p');
        if (gazElement) {
            let currentGaz = parseInt(gazElement.textContent);
            let variation = Math.floor(Math.random() * 6) - 3; // -3 à +3 ppm
            let newGaz = currentGaz + variation;
            gazElement.innerHTML = `${newGaz} <span style="font-size: 1.5rem; color: var(--text-muted);">ppm</span>`;
        }
    }, 3000); // S'exécute toutes les 3 secondes

    // 2. Animation au clic sur le bouton du moteur
    const motorBtn = document.querySelector('.btn-cyber[href*="type=moteur"]');
    if (motorBtn) {
        motorBtn.addEventListener('click', (e) => {
            // On affiche une alerte stylisée dans la console pour le debug de la carte électronique
            console.log("⚡ [ACTION] Ordre de rotation transmis au rotor de distribution.");
        });
    }
});