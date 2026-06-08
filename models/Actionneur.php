<?php

namespace models;
class Actionneur
{
    private $conn;

    public function __construct($db)
    {
        $this->conn = $db;
    }

    // Mettre à jour la valeur ou l'état d'un actionneur dans la BDD
    public function updateStatus($deviceName, $value)
    {
        // Étape 1 : Trouver l'ID de l'actionneur
        $queryFind = "SELECT id FROM devices WHERE name = :name AND type = 'actuator' LIMIT 1";
        $stmtFind = $this->conn->prepare($queryFind);
        $stmtFind->bindParam(":name", $deviceName);
        $stmtFind->execute();
        $device = $stmtFind->fetch(PDO::FETCH_ASSOC);

        if ($device) {
            // Étape 2 : Insérer le nouvel ordre dans l'historique pour que la carte électronique le lise
            $queryInsert = "INSERT INTO device_history (device_id, value_recorded) VALUES (:device_id, :value)";
            $stmtInsert = $this->conn->prepare($queryInsert);
            $stmtInsert->bindParam(":device_id", $device['id']);
            $stmtInsert->bindParam(":value", $value);
            return $stmtInsert->execute();
        }
        return false;
    }
}