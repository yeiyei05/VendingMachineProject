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

    public function getSensorData($name, $fallbackValue)
    {
        $data = $this->capteurModel->getLatestValue($name);
        return $data ? $data['value_recorded'] : $fallbackValue;
    }
}