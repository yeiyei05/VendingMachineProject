<div class="cyber-card auth-card">
    <h2 style="margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 8px var(--neon-blue);">Connexion</h2>

    <?php if (!empty($error_message)): ?>
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 10px; border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; text-align: center;">
            ⚠️ <?php echo htmlspecialchars($error_message); ?>
        </div>
    <?php endif; ?>

    <?php if (isset($_GET['registered'])): ?>
        <div style="background: rgba(57, 255, 20, 0.1); border: 1px solid var(--neon-green); color: var(--neon-green); padding: 10px; border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; text-align: center;">
            🚀 Compte créé ! Connectez-vous.
        </div>
    <?php endif; ?>

    <form action="index.php?page=login" method="POST">
        <div class="form-group">
            <label>Identifiant</label>
            <input type="text" name="username" class="form-control" required autocomplete="off">
        </div>
        <div class="form-group">
            <label>Mot de passe</label>
            <input type="password" name="password" class="form-control" required>
        </div>
        <button type="submit" class="btn-cyber" style="width: 100%; margin-top: 10px;">Connection</button>
    </form>

    <div style="margin-top: 20px; text-align: center; font-size: 0.9rem;">
        <span style="color: var(--text-muted);">Nouvel utilisateur ?</span>
        <a href="index.php?page=register" style="color: var(--neon-purple); text-decoration: none; font-weight: bold;">Créer mon compte</a>
    </div>
</div>