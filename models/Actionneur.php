<?php

namespace models;
class Actionneur
{
    private $conn;

    public function __construct($db)
    {
        $this->conn = $db;
    }

    public function updateStatus($deviceName, $value)
    {

        $queryFind = "SELECT id FROM devices WHERE name = :name AND type = 'actuator' LIMIT 1";
        $stmtFind = $this->conn->prepare($queryFind);
        $stmtFind->bindParam(":name", $deviceName);
        $stmtFind->execute();
        $device = $stmtFind->fetch(PDO::FETCH_ASSOC);

        if ($device) {

            $queryInsert = "INSERT INTO device_history (device_id, value_recorded) VALUES (:device_id, :value)";
            $stmtInsert = $this->conn->prepare($queryInsert);
            $stmtInsert->bindParam(":device_id", $device['id']);
            $stmtInsert->bindParam(":value", $value);
            return $stmtInsert->execute();
        }
        return false;
    }
}