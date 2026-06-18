<?php
namespace config;

class Database
{
    // BDD utilisateurs: valeurs XAMPP par defaut, surchargeables en hebergement.
    private $host_local = 'localhost';
    private $port_local = '3306';
    private $db_local = 'vending_machine_db';
    private $user_local = 'root';
    private $pass_local = '';

    // BDD ISEP pour les capteurs
    private $host_isep = 'mysql.mrlojnat.fr';
    private $port_isep = '3306';
    private $db_isep = 'app';
    private $user_isep = 'g3b';
    private $pass_isep = 'am$S&y39i$5k%^BV';

    public function __construct()
    {
        $overrideFile = __DIR__ . '/database.local.php';

        if (!is_file($overrideFile)) {
            return;
        }

        $config = require $overrideFile;

        if (!is_array($config)) {
            return;
        }

        if (isset($config['local']) && is_array($config['local'])) {
            $this->host_local = $config['local']['host'] ?? $this->host_local;
            $this->port_local = $config['local']['port'] ?? $this->port_local;
            $this->db_local = $config['local']['database'] ?? $this->db_local;
            $this->user_local = $config['local']['username'] ?? $this->user_local;
            $this->pass_local = $config['local']['password'] ?? $this->pass_local;
        }

        if (isset($config['isep']) && is_array($config['isep'])) {
            $this->host_isep = $config['isep']['host'] ?? $this->host_isep;
            $this->port_isep = $config['isep']['port'] ?? $this->port_isep;
            $this->db_isep = $config['isep']['database'] ?? $this->db_isep;
            $this->user_isep = $config['isep']['username'] ?? $this->user_isep;
            $this->pass_isep = $config['isep']['password'] ?? $this->pass_isep;
        }
    }

    public function getConnection()
    {
        try {
            $conn = new \PDO(
                "mysql:host=" . $this->host_local . ";port=" . $this->port_local . ";dbname=" . $this->db_local . ";charset=utf8",
                $this->user_local,
                $this->pass_local
            );
            $conn->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
            return $conn;
        } catch (\PDOException $e) {
            $this->reportConnectionError('locale', $e);
            return null;
        }
    }

    public function getISEPConnection()
    {
        try {
            $conn = new \PDO(
                "mysql:host=" . $this->host_isep . ";port=" . $this->port_isep . ";dbname=" . $this->db_isep . ";charset=utf8",
                $this->user_isep,
                $this->pass_isep,
                [
                    \PDO::ATTR_PERSISTENT => true,
                    \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION
                ]
            );
            return $conn;
        } catch (\PDOException $e) {
            $this->reportConnectionError('ISEP', $e);
            return null;
        }
    }

    private function reportConnectionError($label, \PDOException $e)
    {
        error_log("Erreur connexion " . $label . " : " . $e->getMessage());

        if (ini_get('display_errors') === '1') {
            echo "Erreur connexion " . $label . " : " . $e->getMessage();
        }
    }
}
