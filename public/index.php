<?php
// public/index.php
error_reporting(E_ALL);
ini_set('display_errors', 1);

use config\Database;
use controllers\AuthController;
use controllers\DashboardController;
use controllers\CapteurController;
use controllers\ActionneurController;

if (function_exists('opcache_reset')) {
    opcache_reset();
}

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// On récupère le dossier parent direct de "public"
$root = dirname(__DIR__) . DIRECTORY_SEPARATOR;

// On charge les fichiers
require_once $root . 'config' . DIRECTORY_SEPARATOR . 'database.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'User.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'Capteur.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'Actionneur.php';

require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'AuthController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'DashboardController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'CapteurController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'ActionneurController.php';

$database = new Database();
$db = $database->getConnection();

$page = isset($_GET['page']) ? $_GET['page'] : 'home';

if (!isset($_SESSION['username']) && !in_array($page, ['login', 'register', 'home'])) {
    header('Location: index.php?page=login');
    exit();
}

ob_start();

switch ($page) {
    case 'login':
        $authController = new controllers\AuthController($db);
        $authController->handleLogin();
        break;
    case 'register':
        $authController = new controllers\AuthController($db);
        $authController->handleRegister();
        break;
    case 'logout':
        $authController = new controllers\AuthController($db);
        $authController->logout();
        break;
    case 'home':
        include __DIR__ . '/../views/dashboard/landing.php';
        break;
    case 'dashboard':
        $dashboardController = new controllers\DashboardController($db);
        $dashboardController->showDashboard();
        break;
    case 'dashboard_data':
        $dashboardController = new controllers\DashboardController($db);
        $dashboardController->getDashboardData();
        break;
    case 'capteurs':
        echo '<div class="cyber-card"><h2>⚙️ Console de Configuration</h2><p>Liaison du bus système en cours...</p></div>';
        break;
    default:
        header('Location: index.php?page=home');
        exit();
}

$content = ob_get_clean();

if (isset($_GET['ajax']) && $_GET['ajax'] == '1') {
    echo $content;
} else {
    if (in_array($page, ['login', 'register'])) {
        echo $content;
    } else {
        include __DIR__ . '/../views/layout/main.php';
    }
}
