<?php
namespace controllers;
use models\Capteur;

require_once '../models/Capteur.php';

class CapteurController
{
    private $capteurModel;

    private $distanceVide = 300;
    private $epaisseurProduit = 50;

    public function __construct($db)
    {
        $this->capteurModel = new Capteur($db);
    }

    public function getStock()
    {
        $data = $this->capteurModel->getLatestDistance();
        if ($data) {
            $distance = (int)$data['distance'];
            return $distance;
        }
        return 0;
    }
}