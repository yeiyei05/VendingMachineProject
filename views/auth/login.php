<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - Vending Machine</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .login-container {
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            transition: transform 0.2s;
        }

        h2 {
            text-align: center;
            color: #333333;
            margin-bottom: 2rem;
            font-size: 1.8rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }

        .alert {
            background-color: #fce8e6;
            color: #a8071a;
            padding: 0.8rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            border: 1px solid #f8c2bc;
            text-align: center;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #666666;
            font-size: 0.9rem;
            font-weight: 500;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid #d9d9d9;
            border-radius: 6px;
            font-size: 1rem;
            transition: all 0.2s;
            background-color: #fcfcfc;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #4a90e2;
            background-color: #ffffff;
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
        }

        button {
            width: 100%;
            padding: 0.75rem;
            background-color: #4a90e2;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s;
            margin-top: 0.5rem;
        }

        button:hover {
            background-color: #357abd;
        }

        button:active {
            transform: scale(0.98);
        }

        .form-footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.9rem;
        }

        .form-footer a {
            color: #4a90e2;
            text-decoration: none;
            font-weight: 500;
        }

        .form-footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<div class="login-container">
    <h2>Identification</h2>

    <?php if (!empty($error)): ?>
        <div class="alert">
            <?php echo htmlspecialchars($error); ?>
        </div>
    <?php endif; ?>

    <form action="index.php?page=login" method="POST">
        <div class="form-group">
            <label for="username">Identifiant</label>
            <input type="text" id="username" name="username" placeholder="Votre identifiant" required>
        </div>

        <div class="form-group">
            <label for="password">Mot de passe</label>
            <input type="password" id="password" name="password" placeholder="Votre mot de passe" required>
        </div>

        <button type="submit">Se connecter</button>
    </form>

    <div class="form-footer">
        <p>Nouveau sur la plateforme ? <a href="index.php?page=register">Créer un profil d'accès</a></p>
    </div>
</div>

</body>
</html>