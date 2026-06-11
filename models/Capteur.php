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
        $stmt = $this->conn->prepare(
            "SELECT distance, timestamp FROM distance ORDER BY timestamp DESC LIMIT 1"
        );
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getLatestTemperatureHumidite()
    {
        $stmt = $this->conn->prepare(
            "SELECT temperature, humidite, timestamp FROM temperature_humidite ORDER BY timestamp DESC LIMIT 1"
        );
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getLatestLuminosite()
    {
        $stmt = $this->conn->prepare(
            "SELECT luminosite, timestamp FROM luminosite ORDER BY timestamp DESC LIMIT 1"
        );
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getLatestEmissions()
    {
        $stmt = $this->conn->prepare(
            "SELECT co2_emission, tvoc, timestamp FROM emissions ORDER BY timestamp DESC LIMIT 1"
        );
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getLatestLed()
    {
        $stmt = $this->conn->prepare(
            "SELECT state, timestamp FROM led ORDER BY timestamp DESC LIMIT 1"
        );
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}