<?php
error_reporting(E_ALL);
$httpHost = $_SERVER['HTTP_HOST'] ?? '';
$isLocalHost = preg_match('/^(localhost|127\.0\.0\.1)(:\d+)?$/', $httpHost) === 1;
ini_set('display_errors', $isLocalHost ? '1' : '0');
ini_set('log_errors', '1');

use config\Database;
use controllers\AuthController;
use controllers\DashboardController;
use controllers\CapteurController;
use controllers\ActionneurController;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$root = dirname(__DIR__) . DIRECTORY_SEPARATOR;

$scriptDir = str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'] ?? ''));
$scriptDir = $scriptDir === '/' ? '' : rtrim($scriptDir, '/');
$isPublicEntry = basename($scriptDir) === 'public';

define('APP_BASE_PATH', $scriptDir);
define('APP_ASSET_PATH', $isPublicEntry ? $scriptDir : $scriptDir . '/public');

function app_url(string $page = 'home', array $params = []): string
{
    $query = http_build_query(array_merge(['page' => $page], $params));
    return APP_BASE_PATH . '/index.php' . ($query !== '' ? '?' . $query : '');
}

function app_asset(string $path): string
{
    return APP_ASSET_PATH . '/' . ltrim($path, '/');
}

function app_redirect(string $page = 'home', array $params = [], int $status = 302): void
{
    header('Location: ' . app_url($page, $params), true, $status);
    exit();
}

function app_requested_page(): string
{
    if (!empty($_GET['page'])) {
        return (string) $_GET['page'];
    }

    $path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
    $basePath = APP_BASE_PATH;

    if ($basePath !== '' && strpos($path, $basePath) === 0) {
        $path = substr($path, strlen($basePath));
    }

    $path = trim($path, '/');

    if ($path === '' || $path === 'index.php') {
        return 'home';
    }

    if (strpos($path, 'index.php/') === 0) {
        $path = substr($path, strlen('index.php/'));
    }

    $segments = explode('/', trim($path, '/'));
    return $segments[0] ?? 'home';
}

require_once $root . 'config' . DIRECTORY_SEPARATOR . 'database.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'User.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'Capteur.php';
require_once $root . 'models' . DIRECTORY_SEPARATOR . 'Actionneur.php';

require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'AuthController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'DashboardController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'CapteurController.php';
require_once $root . 'controllers' . DIRECTORY_SEPARATOR . 'ActionneurController.php';

$database = new Database();

$page = preg_replace('/[^a-zA-Z0-9_-]/', '', app_requested_page()) ?: 'home';

if (!isset($_SESSION['username']) && !in_array($page, ['login', 'register', 'home'])) {
    app_redirect('login');
}

ob_start();

switch ($page) {
    case 'login':
        $db = $database->getConnection();
        $authController = new controllers\AuthController($db);
        $authController->handleLogin();
        break;
    case 'register':
        $db = $database->getConnection();
        $authController = new controllers\AuthController($db);
        $authController->handleRegister();
        break;
    case 'logout':
        $authController = new controllers\AuthController(null);
        $authController->logout();
        break;
    case 'home':
        include __DIR__ . '/../views/dashboard/landing.php';
        break;
    case 'dashboard':
        $db_isep = $database->getISEPConnection();
        $dashboardController = new controllers\DashboardController($db_isep);
        $dashboardController->showDashboard();
        break;
    case 'dashboard_data':
        $db_isep = $database->getISEPConnection();
        $dashboardController = new controllers\DashboardController($db_isep);
        $dashboardController->getDashboardData();
        break;
    case 'capteurs':
        $db_isep = $database->getISEPConnection();
        $capteurCtrl = new controllers\CapteurController($db_isep);
        $th    = $capteurCtrl->getTemperatureHumidite();
        $temp  = $th['temperature'] ?? '--';
        $gaz   = $capteurCtrl->getEmissions()['co2_emission'] ?? '--';
        $lux   = $capteurCtrl->getLuminosite();
        $stock = $capteurCtrl->getStock();
        include __DIR__ . '/../views/capteurs/affichage.php';
        include __DIR__ . '/../views/actionneurs/boutons.php';
        break;
    case 'action':
        $db_isep = $database->getISEPConnection();
        $type = $_GET['type'] ?? '';
        $val  = $_POST['val'] ?? $_GET['val'] ?? '';
        $actionneurCtrl = new controllers\ActionneurController($db_isep);
        $actionneurCtrl->changeStatus($type, $val);
        break;
    default:
        app_redirect('home');
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
