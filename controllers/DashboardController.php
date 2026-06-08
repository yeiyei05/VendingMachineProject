<?php

namespace controllers;
use CapteurController;

require_once '../controllers/CapteurController.php';
require_once '../controllers/ActionneurController.php';

class DashboardController
{
    private $db;

    public function __construct($db)
    {
        $this->db = $db;
    }

    public function showDashboard()
    {
        // Vérification de sécurité : l'utilisateur doit être connecté
        if (!isset($_SESSION['user_id'])) {
            header('Location: index.php?page=login');
            exit();
        }

        $capteurCtrl = new CapteurController($this->db);

        // On récupère les vraies données de la BDD (ou valeurs fictives par défaut si la BDD est vide)
        $temp = $capteurCtrl->getSensorData('Capteur Temperature', 4.2);
        $gaz = $capteurCtrl->getSensorData('Capteur Gaz', 120);
        $lux = $capteurCtrl->getSensorData('Capteur Lumiere', 650);

        // On transmet ces variables à la vue
        include '../views/devices/index.php';
    }
}