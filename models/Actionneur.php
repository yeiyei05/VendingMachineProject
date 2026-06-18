<?php
namespace models;

use PDO;

class Actionneur
{
    private $conn;

    public function __construct($db)
    {
        $this->conn = $db;
    }

    public function updateStatus($type, $value)
    {
        if (!$this->conn) {
            return false;
        }

        try {
            switch ($type) {
                case 'moteur':
                    $stmt = $this->conn->prepare(
                        "INSERT INTO moteur (action) VALUES (:action)"
                    );
                    $stmt->bindParam(":action", $value);
                    return $stmt->execute();

                case '7segments':
                    $stmt = $this->conn->prepare(
                        "INSERT INTO segments (source) VALUES (:source)"
                    );
                    $stmt->bindParam(":source", $value);
                    return $stmt->execute();

                default:
                    return false;
            }
        } catch (\PDOException $e) {
            return false;
        }
    }
}
