<?php
// views/dashboard/home.php
$temp = $temp ?? '4.2';
$gaz = $gaz ?? '120';
$lux = $lux ?? '650';
?>

<div style="margin-bottom: 30px;">
    <h1 style="text-shadow: 0 0 10px var(--neon-blue); font-size: 2rem;">VUE D'ENSEMBLE DU RÉSEAU</h1>
    <p style="color: var(--text-muted);">Données télémétriques de l'automate en temps réel.</p>
</div>

<div class="grid-devices">
    <div class="cyber-card">
        <h3>Température Ambiante</h3>
        <p style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-blue); text-shadow: 0 0 8px rgba(0,240,255,0.4);">
            <?php echo htmlspecialchars($temp); ?> °C
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Suivi de la chaîne de fraîcheur des produits.</p>
    </div>

    <div class="cyber-card">
        <h3>Analyse Qualité de l'Air (Gaz)</h3>
        <p style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-purple); text-shadow: 0 0 8px rgba(189,0,255,0.4);">
            <?php echo htmlspecialchars($gaz); ?> ppm
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Détection de sécurité environnementale.</p>
    </div>

    <div class="cyber-card">
        <h3>Luminosité Interne</h3>
        <p style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-green); text-shadow: 0 0 8px rgba(57,255,20,0.4);">
            <?php echo htmlspecialchars($lux); ?> lx
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Contrôle optique des modules de vente.</p>
    </div>
</div>