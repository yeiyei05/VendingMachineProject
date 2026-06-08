<div class="cyber-card" style="border-left-color: var(--neon-purple); box-shadow: 0 5px 15px rgba(189, 0, 255, 0.05);">
    <h3 style="color: var(--neon-purple); margin-top: 0; font-size: 1.2rem; letter-spacing: 1px;">📦 MOTORISATION DE COMMANDE</h3>
    <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.4; margin-bottom: 20px;">
        Déclenche manuellement la rotation de la spirale pour éjecter le produit sélectionné (boisson ou snack frais).
    </p>

    <div style="margin-bottom: 15px;">
        <a href="index.php?page=action&type=moteur&val=1" class="btn-cyber" style="display: block; text-decoration: none; text-align: center; box-shadow: 0 0 10px rgba(189, 0, 255, 0.3);">
            🌀 Activer le Rotor de Distribution
        </a>
    </div>

    <div style="font-size: 0.8rem; color: var(--text-muted); background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; text-align: center;">
        Dernier statut proximité : <span style="color: var(--neon-blue); font-weight: bold;">Produit récupéré ✓</span>
    </div>
</div>

<div class="cyber-card" style="border-left-color: var(--neon-purple); box-shadow: 0 5px 15px rgba(189, 0, 255, 0.05);">
    <h3 style="color: var(--neon-purple); margin-top: 0; font-size: 1.2rem; letter-spacing: 1px;">🔢 FACADE NUMÉRIQUE (7-SEG)</h3>
    <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.4; margin-bottom: 20px;">
        Modifie la valeur numérique affichée sur l'écran LED du distributeur (idéal pour mettre à jour un prix ou afficher un code d'erreur).
    </p>

    <form action="index.php?page=action&type=7segments" method="POST" style="display: flex; gap: 12px; align-items: center;">
        <div style="flex-grow: 1;">
            <input type="number" name="val" class="form-control" placeholder="Ex: 150 (Yens)" min="0" max="999" required
                   style="font-family: monospace; font-size: 1.1rem; text-align: center; letter-spacing: 2px;">
        </div>
        <div>
            <button type="submit" class="btn-cyber" style="padding: 12px 20px;">
                ⚙️ Injecter
            </button>
        </div>
    </form>

    <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
        Mode d'affichage actif : <span style="color: #fff; font-family: monospace;">Tarification Standard</span>
    </div>
</div>