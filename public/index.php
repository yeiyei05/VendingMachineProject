<?php
// public/index.php
use config\Database;
use controllers\AuthController;
use controllers\DashboardController;

if (function_exists('opcache_reset')) {
    opcache_reset();
}

if (session_status() === PHP_SESSION_NONE) {
    session_start();
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

$page = isset($_GET['page']) ? $_GET['page'] : 'dashboard';

if (!isset($_SESSION['username']) && !in_array($page, ['login', 'register'])) {
    header('Location: index.php?page=login');
    exit();
}

switch ($page) {
    case 'login':
        $authController = new AuthController($db);
        $authController->login();
        break;
    case 'register':
        $authController = new AuthController($db);
        $authController->register();
        break;
    case 'logout':
        $authController = new AuthController($db);
        $authController->logout();
        break;
    case 'dashboard':
        $dashboardController = new DashboardController($db);
        $dashboardController->index();
        break;
    default:
        header('Location: index.php?page=dashboard');
        exit();
}