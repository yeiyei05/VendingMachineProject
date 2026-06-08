<?php
// config/database.php

namespace config;
class Database
{
    // Configuration des identifiants par défaut pour XAMPP
    private $host = "localhost";
    private $db_name = "vending_machine_db"; // Le nom de ta base SQL sur phpMyAdmin
    private $username = "root";              // Identifiant par défaut XAMPP
    private $password = "";                  // Pas de mot de passe par défaut sur XAMPP
    public $conn;

    // Fonction pour initialiser la connexion
    public function getConnection()
    {
        $this->conn = null;
        try {
            // Création de la connexion avec prise en charge de l'UTF-8 pour éviter les bugs d'accents
            $this->conn = new \PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name . ";charset=utf8",
                $this->username,
                $this->password
            );
            // Activation des alertes d'erreurs SQL pour le développement
            $this->conn->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
        } catch (\PDOException $exception) {
            echo "Erreur de connexion au serveur SQL : " . $exception->getMessage();
        }
        return $this->conn;
    }
}