<?php
namespace controllers;

use models\Actionneur;

require_once '../models/Actionneur.php';

class ActionneurController
{
    private $actionneurModel;

    public function __construct($db)
    {
        $this->actionneurModel = new Actionneur($db);
    }

    public function changeStatus($type, $value)
    {
        $this->actionneurModel->updateStatus($type, $value);
        header('Location: index.php?page=capteurs');
        exit();
    }
}