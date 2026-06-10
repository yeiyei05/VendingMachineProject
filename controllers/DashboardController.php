<?php
namespace controllers;

class DashboardController {
    private $db;

    public function index($db) {
        $this->db = $db;

        // Gestion de la session en toute sécurité
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }

        // On vérifie les deux clés possibles par précaution
        if (!isset($_SESSION['user_id']) && !isset($_SESSION['username'])) {
            header('Location: index.php?page=login');
            exit();
        }

        // Récupération des capteurs
        $capteurCtrl = new CapteurController($this->db);
        $temp = $capteurCtrl->getSensorData('Capteur Temperature', 4.2);
        $gaz = $capteurCtrl->getSensorData('Capteur Gaz', 120);
        $lux = $capteurCtrl->getSensorData('Capteur Lumiere', 650);

        // 🚀 C'est cette ligne qui inclut ton design home.php !
        include __DIR__ . '/../views/dashboard/home.php';
    }
}