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

        $values = $this->getDashboardValues();
        $stock = $values['stock'];

        include __DIR__ . '/../views/dashboard/home.php';
    }

    public function getDashboardData()
    {
        if (!isset($_SESSION['user_id']) && !isset($_SESSION['username'])) {
            http_response_code(401);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'Non authentifie']);
            exit();
        }

        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($this->getDashboardValues());
        exit();
    }

    private function getDashboardValues()
    {
        $capteurCtrl = new CapteurController($this->db);
        return [
            'stock' => $capteurCtrl->getStock(),
        ];
    }

    public function showLanding()
    {
        include __DIR__ . '/../views/dashboard/landing.php';
    }
}