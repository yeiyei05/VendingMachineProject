<?php
$stock = $stock ?? '0';
$stockNumber = (int)$stock;
$stockIsLow = $stockNumber <= 3;
$stockLevel = max(0, min(100, ($stockNumber / 5) * 100));
$stockStatus = $stockIsLow ? 'À recharger' : 'Opérationnel';
$stockMessage = $stockIsLow
    ? 'Stock bas détecté. Planifier un remplissage du distributeur.'
    : 'Niveau de stock stable, détecté par le capteur HC-SR04.';
?>

<section class="dashboard-stock-shell" id="dashboard-live-data" data-refresh-url="index.php?page=dashboard_data">
    <div class="dashboard-hero">
        <div>
            <span class="dashboard-eyebrow">Pilotage temps réel</span>
            <h1>Stock Distributeur</h1>
            <p>Suivi professionnel du niveau disponible dans le distributeur connecté.</p>
        </div>

        <span class="status-pill <?= $stockIsLow ? 'is-low' : 'is-ready' ?>" id="stock-status">
            <?= htmlspecialchars($stockStatus) ?>
        </span>
    </div>

    <article class="stock-panel <?= $stockIsLow ? 'is-low' : 'is-ready' ?>" id="stock-card">
        <div class="stock-panel__header">
            <div>
                <span class="stock-panel__label">Donnée affichée</span>
                <h2>Stock Distributeur</h2>
            </div>
            <div class="stock-panel__icon" aria-hidden="true">SD</div>
        </div>

        <div class="stock-metric">
            <span class="stock-metric__value" id="stock-value"><?= htmlspecialchars($stock) ?></span>
            <span class="stock-metric__unit">aliments</span>
        </div>

        <div class="stock-progress" aria-hidden="true">
            <span id="stock-fill" style="width: <?= $stockLevel ?>%;"></span>
        </div>

        <p class="stock-message" id="stock-message"><?= htmlspecialchars($stockMessage) ?></p>

        <div class="stock-meta">
            <span>Source: HC-SR04</span>
            <span>Actualisation automatique</span>
        </div>
    </article>
</section>
