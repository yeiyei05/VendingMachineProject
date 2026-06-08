<div style="max-width: 450px; margin: 60px auto;">
    <div class="cyber-card" style="border-left-color: var(--neon-blue); box-shadow: 0 0 25px rgba(0, 240, 255, 0.15);">
        <h2 style="text-align: center; margin-bottom: 30px; text-shadow: 0 0 8px var(--neon-blue);">ENREGISTREMENT NOUVEL AGENT</h2>

        <?php if(isset($error)): ?>
            <div style="color: #ff0055; margin-bottom: 15px; text-align: center;"><?= $error ?></div>
        <?php endif; ?>
        <?php if(isset($success)): ?>
            <div style="color: var(--neon-green); margin-bottom: 15px; text-align: center;"><?= $success ?></div>
        <?php endif; ?>

        <form action="index.php?page=register" method="POST">
            <div class="form-group">
                <label>Nom d'Agent</label>
                <input type="text" name="username" class="form-control" placeholder="Tanaka_99" required>
            </div>
            <div class="form-group">
                <label>Cyber-Email</label>
                <input type="email" name="email" class="form-control" placeholder="tanaka@isep.fr" required>
            </div>
            <div class="form-group">
                <label>Clé Secrète (Mot de passe)</label>
                <input type="password" name="password" class="form-control" placeholder="••••••••" required>
            </div>
            <div style="margin-top: 30px;">
                <button type="submit" class="btn-cyber" style="width: 100%;">Générer les Accès</button>
            </div>
        </form>
        <p style="text-align: center; margin-top: 20px; font-size: 0.85rem; color: var(--text-muted);">
            Déjà inscrit ? <a href="index.php?page=login" style="color: var(--neon-purple); text-decoration: none;">S'identifier</a>
        </p>
    </div>
</div>