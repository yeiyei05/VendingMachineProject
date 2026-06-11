<?php
namespace controllers;
use models\Capteur;

require_once '../models/Capteur.php';

class CapteurController
{
    private $capteurModel;

    public function __construct($db)
    {
        $this->capteurModel = new Capteur($db);
    }

    public function getStock()
    {
        $data = $this->capteurModel->getLatestDistance();
        return $data ? (int)$data['distance'] : 0;
    }

    public function getTemperatureHumidite()
    {
        $data = $this->capteurModel->getLatestTemperatureHumidite();
        return $data ? $data : ['temperature' => '--', 'humidite' => '--'];
    }

    public function getLuminosite()
    {
        $data = $this->capteurModel->getLatestLuminosite();
        return $data ? (float)$data['luminosite'] : '--';
    }

    public function getEmissions()
    {
        $data = $this->capteurModel->getLatestEmissions();
        return $data ? $data : ['co2_emission' => '--', 'tvoc' => '--'];
    }

    public function getLed()
    {
        $data = $this->capteurModel->getLatestLed();
        return $data ? (bool)$data['state'] : false;
    }
}