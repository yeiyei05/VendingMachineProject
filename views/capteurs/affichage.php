<div class="cyber-card" style="border-left-color: var(--neon-blue); box-shadow: 0 5px 15px rgba(0, 240, 255, 0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h3 style="margin: 0; color: var(--neon-blue); font-size: 1.1rem; letter-spacing: 1px;">🌡️ ZONE FRAÎCHEUR</h3>
        <span style="color: var(--neon-green); font-weight: bold; font-size: 0.8rem; text-shadow: 0 0 5px var(--neon-green);">● EN LIGNE</span>
    </div>
    <p style="font-size: 2.5rem; font-weight: bold; margin: 15px 0; font-family: monospace; text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);">
        <?= htmlspecialchars($temp); ?> <span style="font-size: 1.5rem; color: var(--text-muted);">°C</span>
    </p>
    <div style="font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px; margin-top: 10px;">
        Contrôle climat : <span style="color: #fff;">Optimisé (Légumes/Snacks)</span>
    </div>
</div>

<div class="cyber-card" style="border-left-color: var(--neon-green); box-shadow: 0 5px 15px rgba(57, 255, 20, 0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h3 style="margin: 0; color: var(--neon-green); font-size: 1.1rem; letter-spacing: 1px;">💨 ANALYSE DE GAZ</h3>
        <span style="color: var(--neon-green); font-weight: bold; font-size: 0.8rem; text-shadow: 0 0 5px var(--neon-green);">● EN LIGNE</span>
    </div>
    <p style="font-size: 2.5rem; font-weight: bold; margin: 15px 0; font-family: monospace; text-shadow: 0 0 10px rgba(57, 255, 20, 0.4);">
        <?= htmlspecialchars($gaz); ?> <span style="font-size: 1.5rem; color: var(--text-muted);">ppm</span>
    </p>
    <div style="font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px; margin-top: 10px;">
        Qualité de l'air : <span style="color: var(--neon-green);">Sain (Aucune anomalie)</span>
    </div>
</div>

<div class="cyber-card" style="border-left-color: #ffaa00; box-shadow: 0 5px 15px rgba(255, 170, 0, 0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h3 style="margin: 0; color: #ffaa00; font-size: 1.1rem; letter-spacing: 1px;">☀️ LUMINOSITÉ VITRINE</h3>
        <span style="color: var(--neon-green); font-weight: bold; font-size: 0.8rem; text-shadow: 0 0 5px var(--neon-green);">● EN LIGNE</span>
    </div>
    <p style="font-size: 2.5rem; font-weight: bold; margin: 15px 0; font-family: monospace; text-shadow: 0 0 10px rgba(255, 170, 0, 0.4);">
        <?= htmlspecialchars($lux); ?> <span style="font-size: 1.5rem; color: var(--text-muted);">Lux</span>
    </p>
    <div style="font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px; margin-top: 10px;">
        Éclairage d'ambiance : <span style="color: #fff;">Ajustement Automatique</span>
    </div>
</div>