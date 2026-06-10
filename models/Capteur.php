<?php

namespace models;
use PDO;

class Capteur
{
    private $conn;

    public function __construct($db)
    {
        $this->conn = $db;
    }

    // Récupérer la dernière valeur d'un capteur spécifique (par son ID ou Nom)
    public function getLatestValue($deviceName)
    {
        $query = "SELECT dh.value_recorded, dh.timestamp 
                  FROM device_history dh
                  JOIN devices d ON dh.device_id = d.id
                  WHERE d.name = :name AND d.type = 'sensor'
                  ORDER BY dh.timestamp DESC LIMIT 1";

        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(":name", $deviceName);
        $stmt->execute();

        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}