<div class="cyber-card auth-card">
    <h2 style="margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 8px var(--neon-purple); text-align: center;">Enregistrement Agent</h2>

    <?php if (!empty($error_message)): ?>
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 10px; border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; text-align: center;">
            ⚠️ <?php echo htmlspecialchars($error_message); ?>
        </div>
    <?php endif; ?>

    <form action="index.php?page=register" method="POST">
        <div class="form-group" style="margin-bottom: 15px;">
            <label style="color: var(--neon-blue); display: block; margin-bottom: 5px; font-size: 0.85rem; text-transform: uppercase;">Créer Identifiant</label>
            <input type="text" name="username" class="form-control" required autocomplete="off" style="width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 4px; color: #fff;">
        </div>

        <div class="form-group" style="margin-bottom: 20px;">
            <label style="color: var(--neon-blue); display: block; margin-bottom: 5px; font-size: 0.85rem; text-transform: uppercase;">Créer le mot de passe</label>
            <input type="password" name="password" class="form-control" required style="width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 4px; color: #fff;">
        </div>

        <button type="submit" class="btn-cyber" style="width: 100%; padding: 12px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue)); color: white; text-transform: uppercase;">Créer mon compte</button>
    </form>

    <div style="margin-top: 20px; text-align: center; font-size: 0.9rem;">
        <span style="color: var(--text-muted);">Vous avez déjà un compte ?</span>
        <a href="index.php?page=login" style="color: #00ffcc; text-decoration: none; font-weight: bold;">Se connecter</a>
    </div>
</div>