<?php
// public/index.php
session_start();

// --- CONFIGURATION BASE DE DONNÉES LOCALHOST (XAMPP) ---
$host = 'localhost';
$dbname = 'vending_machine_db';
$username = 'root';
$password = '';

$db_error = null;

try {
    $db = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    $db = null;
    // On stocke le vrai message d'erreur SQL pour le voir à l'écran
    $db_error = "Connexion BDD échouée : " . $e->getMessage();
}

// Détermination de la page
$page = isset($_GET['page']) ? $_GET['page'] : 'home';
$error_message = null;

/* ==========================================================================
   🛠️ MÉMOIRE DE LA PAGE PRÉCÉDENTE (Pour le bouton Annuler)
   ========================================================================== */
if ($page !== 'logout' && $page !== 'logout_execute') {
    $_SESSION['last_active_page'] = $page;
}
// Si on clique sur annuler, on retourne sur la dernière page ou par défaut sur 'home'
$previous_page = isset($_SESSION['last_active_page']) ? $_SESSION['last_active_page'] : 'home';


// Sécurité : Si pas connecté, accès restreint uniquement à home, login, register et logout_execute
$pages_publiques = ['home', 'login', 'register', 'logout_execute'];
if (!isset($_SESSION['user_id']) && !in_array($page, $pages_publiques)) {
    header('Location: index.php?page=login');
    exit();
}

// Enclenchement de la mémoire tampon
ob_start();

switch ($page) {
    case 'login':
        if ($db_error) { $error_message = $db_error; }

        // 🔑 TRAITEMENT DU FORMULAIRE DE CONNEXION
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && !$db_error) {
            $user_input = isset($_POST['username']) ? trim($_POST['username']) : '';
            $pass_input = isset($_POST['password']) ? $_POST['password'] : '';

            if (!empty($user_input) && !empty($pass_input)) {
                $stmt = $db->prepare("SELECT * FROM users WHERE username = ?");
                $stmt->execute([$user_input]);
                $user = $stmt->fetch(PDO::FETCH_ASSOC);

                if ($user && password_verify($pass_input, $user['password'])) {
                    $_SESSION['user_id'] = $user['id'];
                    $_SESSION['username'] = $user['username'];

                    header('Location: index.php?page=home');
                    exit();
                } else {
                    $error_message = "Identifiant ou code d'accès incorrect.";
                }
            } else {
                $error_message = "Veuillez remplir tous les champs.";
            }
        }
        include __DIR__ . '/../views/auth/login.php';
        break;

    case 'register':
        if ($db_error) { $error_message = $db_error; }

        // 📝 TRAITEMENT DU FORMULAIRE D'INSCRIPTION
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && !$db_error) {
            $user_input = isset($_POST['username']) ? trim($_POST['username']) : '';
            $pass_input = isset($_POST['password']) ? $_POST['password'] : '';

            if (!empty($user_input) && !empty($pass_input)) {
                $check = $db->prepare("SELECT id FROM users WHERE username = ?");
                $check->execute([$user_input]);

                if ($check->fetch()) {
                    $error_message = "Cet identifiant agent est déjà attribué.";
                } else {
                    $hashed_password = password_hash($pass_input, PASSWORD_BCRYPT);
                    $stmt = $db->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
                    $stmt->execute([$user_input, $hashed_password]);

                    header('Location: index.php?page=login&registered=1');
                    exit();
                }
            } else {
                $error_message = "Erreur d'inscription. Données incomplètes.";
            }
        }
        include __DIR__ . '/../views/auth/register.php';
        break;

    case 'logout':
        $current_agent = isset($_SESSION['username']) ? htmlspecialchars($_SESSION['username']) : 'Agent';
        echo '
        <div class="cyber-card auth-card logout-card">
            <h2 class="logout-title">⚠️ Déconnexion Système</h2>
            
            <p class="logout-text">
                Attention <strong class="logout-agent">' . $current_agent . '</strong>, vous êtes sur le point de couper la liaison avec la console de configuration.<br>
                Voulez-vous vraiment vous déconnecter ?
            </p>
            
            <div class="logout-actions">
                <button onclick="window.location.href=\'index.php?page=logout_execute\';" class="btn-logout-confirm">
                    Oui, me déconnecter
                </button>
                
                <a href="index.php?page=' . $previous_page . '" class="btn-logout-cancel">
                    Annuler
                </a>
            </div>
        </div>';
        break;

    case 'logout_execute':
        // ⚡ NETTOYAGE ABSOLU DE LA SESSION ET DES COOKIES COMPAGNONS
        $_SESSION = array();
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $params["path"], $params["domain"],
                $params["secure"], $params["httponly"]
            );
        }
        session_destroy();

        // 🚀 CORRECTION : Changement de cible pour atterrir directement sur la mire de connexion
        header('Location: index.php?page=login');
        exit();

    case 'home':
        include __DIR__ . '/../views/dashboard/landing.php';
        break;

    case 'dashboard':
        include __DIR__ . '/../views/dashboard/home.php';
        break;

    case 'capteurs':
        echo '
        <div style="margin-bottom: 30px;">
            <h1 style="text-shadow: 0 0 10px var(--neon-blue); font-size: 2rem;">CONSOLE DE CONFIGURATION</h1>
            <p style="color: var(--text-muted);">Gestion des bus systèmes et actionneurs matériels.</p>
        </div>
        <div class="cyber-card">
            <h3 style="color: var(--neon-purple); margin-bottom: 15px;">⚙️ Liaison des Matériels IoT</h3>
            <p style="color: var(--text-color); line-height: 1.6;">Le bus système est actuellement en attente d\'instructions de synchronisation avec l\'automate physique.</p>
        </div>';
        break;

    default:
        header('Location: index.php?page=home');
        exit();
}

$content = ob_get_clean();

// --- RENDU DYNAMIQUE (SPA) ---
if (isset($_GET['ajax']) && $_GET['ajax'] == '1') {
    echo $content;
} else {
    if ($page === 'login' || $page === 'register') {
        include __DIR__ . '/../views/layout/auth_layout.php';
    } else {
        include __DIR__ . '/../views/layout/main.php';
    }
}