<?php
namespace config;

class Database
{
    private $host = 'mysql.mrlojnat.fr';
    private $port = '3306';
    private $db_name = 'app';
    private $username = 'g3b';
    private $password = 'am$S&y39i$5k%^BV';
    public $conn;

    public function getConnection()
    {
        $this->conn = null;
        try {
            $this->conn = new \PDO(
                "mysql:host=" . $this->host . ";port=" . $this->port . ";dbname=" . $this->db_name . ";charset=utf8",
                $this->username,
                $this->password
            );
            $this->conn->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
        } catch (\PDOException $exception) {
            echo "Erreur de connexion au serveur SQL : " . $exception->getMessage();
        }
        return $this->conn;
    }
}