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
            \app_redirect('login');
        }

        $values = $this->getDashboardValues();
        $stock       = $values['stock'];
        $distance    = $values['distance'];
        $temp        = $values['temperature'];
        $humidite    = $values['humidite'];
        $luminosite  = $values['luminosite'];
        $co2         = $values['co2'];
        $tvoc        = $values['tvoc'];
        $led         = $values['led'];

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
        $th = $capteurCtrl->getTemperatureHumidite();
        $em = $capteurCtrl->getEmissions();

        return [
            'stock'       => $capteurCtrl->getStock(),
            'distance'    => $capteurCtrl->getDistance(),
            'temperature' => $th['temperature'],
            'humidite'    => $th['humidite'],
            'luminosite'  => $capteurCtrl->getLuminosite(),
            'co2'         => $em['co2_emission'],
            'tvoc'        => $em['tvoc'],
            'led'         => $capteurCtrl->getLed(),
        ];
    }

    public function showLanding()
    {
        include __DIR__ . '/../views/dashboard/landing.php';
    }
}
