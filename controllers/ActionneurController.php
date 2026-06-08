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

    public function changeStatus($name, $value)
    {
        $this->actionneurModel->updateStatus($name, $value);
        header('Location: index.php?page=dashboard');
        exit();
    }
}