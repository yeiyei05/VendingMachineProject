<?php
namespace controllers;

require_once __DIR__ . '/../controllers/CapteurController.php';

class DashboardController
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function showDashboard()
    {
        if (!isset($_SESSION['user_id']) && !isset($_SESSION['username'])) {
            header('Location: index.php?page=login');
            exit();
        }

        $capteurCtrl = new CapteurController($this->db);
        $temp  = $capteurCtrl->getSensorData('Capteur Temperature', 4.2);
        $gaz   = $capteurCtrl->getSensorData('Capteur Gaz', 120);
        $lux   = $capteurCtrl->getSensorData('Capteur Lumiere', 650);
        $stock = $capteurCtrl->getSensorData('HC-SR04', 0);

        include __DIR__ . '/../views/dashboard/home.php';
    }

    public function showLanding()
    {
        include __DIR__ . '/../views/dashboard/landing.php';
    }
}