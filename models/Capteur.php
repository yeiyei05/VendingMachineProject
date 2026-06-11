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

    public function getLatestDistance()
    {
        $query = "SELECT distance, timestamp
                  FROM distance
                  ORDER BY timestamp DESC LIMIT 1";

        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}