<?php
$temp  = $temp  ?? '4.2';
$gaz   = $gaz   ?? '120';
$lux   = $lux   ?? '650';
$stock = $stock ?? '0';
$stockBas = (int)$stock <= 3;
?>

<div style="margin-bottom: 30px;">
    <h1 style="text-shadow: 0 0 10px var(--neon-blue); font-size: 2rem;">VUE D'ENSEMBLE DU RÉSEAU</h1>
    <p style="color: var(--text-muted);">Données télémétriques de la Vending Machine en temps réel.</p>
</div>

<div class="grid-devices" id="dashboard-live-data" data-refresh-url="index.php?page=dashboard_data">

    <div class="cyber-card" id="stock-card" style="border-left-color: <?= $stockBas ? '#ff4444' : 'var(--neon-green)' ?>;">
        <h3>📦 Stock Distributeur A</h3>
        <p id="stock-value" style="font-size: 2.2rem; font-weight: bold; margin: 15px 0;
                  color: <?= $stockBas ? '#ff4444' : 'var(--neon-green)' ?>;
                  text-shadow: 0 0 8px rgba(57,255,20,0.4);">
            <?= htmlspecialchars($stock) ?> <span style="font-size: 1.2rem;">aliments</span>
        </p>
        <?php if ($stockBas): ?>
            <p style="color: #ff4444; font-size: 0.9rem;">⚠️ Stock bas — remplissage requis</p>
        <?php else: ?>
            <p style="color: var(--text-muted); font-size: 0.9rem;">Niveau détecté par HC-SR04.</p>
        <?php endif; ?>
    </div>

    <div class="cyber-card">
        <h3>🌡️ Température Ambiante</h3>
        <p id="sensor-temp" style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-blue); text-shadow: 0 0 8px rgba(0,240,255,0.4);">
            <?= htmlspecialchars($temp) ?> °C
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Suivi de la chaîne de fraîcheur des produits.</p>
    </div>

    <div class="cyber-card">
        <h3>💨 Analyse Qualité de l'Air (Gaz)</h3>
        <p id="sensor-gaz" style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-purple); text-shadow: 0 0 8px rgba(189,0,255,0.4);">
            <?= htmlspecialchars($gaz) ?> ppm
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Détection de sécurité et décomposition.</p>
    </div>

    <div class="cyber-card">
        <h3>💡 Luminosité Interne</h3>
        <p id="sensor-lux" style="font-size: 2.2rem; font-weight: bold; margin: 15px 0; color: var(--neon-green); text-shadow: 0 0 8px rgba(57,255,20,0.4);">
            <?= htmlspecialchars($lux) ?> lx
        </p>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Contrôle optique des sas de distribution.</p>
    </div>

</div>
