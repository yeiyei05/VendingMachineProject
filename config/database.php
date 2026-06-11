<?php
namespace config;

class Database
{
    // BDD locale pour les utilisateurs
    private $host_local = 'localhost';
    private $db_local = 'vending_machine_db';
    private $user_local = 'root';
    private $pass_local = '';

    // BDD ISEP pour les capteurs
    private $host_isep = 'mysql.mrlojnat.fr';
    private $port_isep = '3306';
    private $db_isep = 'app';
    private $user_isep = 'g3b';
    private $pass_isep = 'am$S&y39i$5k%^BV';

    public function getConnection()
    {
        try {
            $conn = new \PDO(
                "mysql:host=" . $this->host_local . ";dbname=" . $this->db_local . ";charset=utf8",
                $this->user_local,
                $this->pass_local
            );
            $conn->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
            return $conn;
        } catch (\PDOException $e) {
            echo "Erreur connexion locale : " . $e->getMessage();
            return null;
        }
    }

    public function getISEPConnection()
    {
        try {
            $conn = new \PDO(
                "mysql:host=" . $this->host_isep . ";port=" . $this->port_isep . ";dbname=" . $this->db_isep . ";charset=utf8",
                $this->user_isep,
                $this->pass_isep
            );
            $conn->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
            return $conn;
        } catch (\PDOException $e) {
            echo "Erreur connexion ISEP : " . $e->getMessage();
            return null;
        }
    }
}