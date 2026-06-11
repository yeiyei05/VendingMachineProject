<?php
$stock      = $stock      ?? 0;
$temp       = $temp       ?? '--';
$humidite   = $humidite   ?? '--';
$luminosite = $luminosite ?? '--';
$co2        = $co2        ?? '--';
$tvoc       = $tvoc       ?? '--';
$led        = $led        ?? false;

$stockNumber = (int)$stock;
$stockIsLow  = $stockNumber <= 3;
$stockLevel  = max(0, min(100, ($stockNumber / 5) * 100));
$stockStatus = $stockIsLow ? 'À recharger' : 'Opérationnel';
$stockMessage = $stockIsLow
    ? 'Stock bas détecté. Planifier un remplissage du distributeur.'
    : 'Niveau de stock stable, détecté par le capteur HC-SR04.';
?>

<section class="dashboard-stock-shell" id="dashboard-live-data" data-refresh-url="index.php?page=dashboard_data">

    <div class="dashboard-hero">
        <div>
            <span class="dashboard-eyebrow">Pilotage temps réel</span>
            <h1>Vue d'ensemble du réseau</h1>
            <p>Données télémétriques de tous les capteurs connectés.</p>
        </div>
        <span class="status-pill <?= $stockIsLow ? 'is-low' : 'is-ready' ?>" id="stock-status">
            <?= htmlspecialchars($stockStatus) ?>
        </span>
    </div>

    <div class="grid-devices">

        <!-- Stock HC-SR04 -->
        <article class="stock-panel <?= $stockIsLow ? 'is-low' : 'is-ready' ?>" id="stock-card">
            <div class="stock-panel__header">
                <div>
                    <span class="stock-panel__label">Votre capteur</span>
                    <h2>Stock Distributeur</h2>
                </div>
                <div class="stock-panel__icon">SD</div>
            </div>
            <div class="stock-metric">
                <span class="stock-metric__value" id="stock-value"><?= htmlspecialchars($stock) ?></span>
                <span class="stock-metric__unit">aliments</span>
            </div>
            <div class="stock-progress">
                <span id="stock-fill" style="width: <?= $stockLevel ?>%;"></span>
            </div>
            <p class="stock-message" id="stock-message"><?= htmlspecialchars($stockMessage) ?></p>
            <div class="stock-meta">
                <span>Source: HC-SR04</span>
                <span>Actualisation automatique</span>
            </div>
        </article>

        <!-- Température & Humidité -->
        <article class="stock-panel is-ready">
            <div class="stock-panel__header">
                <div>
                    <span class="stock-panel__label">Capteur ambiance</span>
                    <h2>Température & Humidité</h2>
                </div>
                <div class="stock-panel__icon">TH</div>
            </div>
            <div class="stock-metric">
                <span class="stock-metric__value stock-metric__value--sm" style="font-size: 4.5rem; white-space: nowrap;"><?= htmlspecialchars($temp) ?></span>
                <span class="stock-metric__unit">°C</span>
            </div>
            <p class="stock-message">Humidité : <?= htmlspecialchars($humidite) ?> %</p>
            <div class="stock-meta">
                <span>Suivi environnemental en temps réel</span>
            </div>
        </article>

        <!-- Luminosité -->
        <article class="stock-panel is-ready">
            <div class="stock-panel__header">
                <div>
                    <span class="stock-panel__label">Capteur optique</span>
                    <h2>Luminosité</h2>
                </div>
                <div class="stock-panel__icon">LX</div>
            </div>
            <div class="stock-metric">
                <span class="stock-metric__value stock-metric__value--sm" style="font-size: 4.5rem; white-space: nowrap;"><?= htmlspecialchars($luminosite) ?></span>
                <span class="stock-metric__unit">lx</span>
            </div>
            <p class="stock-message">Contrôle optique des sas de distribution.</p>
            <div class="stock-meta">
                <span>Source: Capteur luminosité</span>
            </div>
        </article>

        <!-- Qualité de l'Air -->
        <article class="stock-panel is-ready">
            <div class="stock-panel__header">
                <div>
                    <span class="stock-panel__label">Capteur air</span>
                    <h2>Qualité de l'Air</h2>
                </div>
                <div class="stock-panel__icon">CO2</div>
            </div>
            <div class="stock-metric">
                <span class="stock-metric__value stock-metric__value--sm" style="font-size: 4.5rem; white-space: nowrap;"><?= htmlspecialchars($co2) ?></span>
                <span class="stock-metric__unit">ppm CO₂</span>
            </div>
            <p class="stock-message">TVOC : <?= htmlspecialchars($tvoc) ?> ppb</p>
            <div class="stock-meta">
                <span>Détection sécurité et décomposition</span>
            </div>
        </article>

        <!-- LED -->
        <article class="stock-panel <?= $led ? 'is-ready' : 'is-low' ?>">
            <div class="stock-panel__header">
                <div>
                    <span class="stock-panel__label">Actionneur</span>
                    <h2>État LED</h2>
                </div>
                <div class="stock-panel__icon">LED</div>
            </div>
            <div class="stock-metric">
                <span class="stock-metric__value stock-metric__value--sm" style="font-size: 4.5rem; white-space: nowrap;"><?= $led ? 'Allumée' : 'Éteinte' ?></span>
            </div>
            <p class="stock-message"><?= $led ? 'LED active — signal opérationnel.' : 'LED inactive.' ?></p>
            <div class="stock-meta">
                <span>Actionneur LED du groupe</span>
            </div>
        </article>

    </div>

</section>