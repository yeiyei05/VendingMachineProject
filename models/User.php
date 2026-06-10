<?php

namespace models;
use PDO;
class User
{
    private $conn;
    private $table_name = "users";

    public function __construct($db)
    {
        $this->conn = $db;
    }

    // Inscription d'un nouvel utilisateur
    public function register($username, $email, $password)
    {
        $query = "INSERT INTO " . $this->table_name . " (username, email, password) VALUES (:username, :email, :password)";
        $stmt = $this->conn->prepare($query);

        // Hachage de sécurité pour le mot de passe
        $hashed_password = password_hash($password, PASSWORD_BCRYPT);

        $stmt->bindParam(":username", $username);
        $stmt->bindParam(":email", $email);
        $stmt->bindParam(":password", $hashed_password);

        return $stmt->execute();
    }

    // Connexion
    public function login($username, $password)
    {
        $query = "SELECT id, username, password FROM " . $this->table_name . " WHERE username = :username LIMIT 0,1";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(":username", $username);
        $stmt->execute();

        if ($stmt->rowCount() > 0) {
            $row = $stmt->fetch(\PDO::FETCH_ASSOC);
            if (password_verify($password, $row['password'])) {
                return $row; // Connexion réussie, on renvoie les infos de l'utilisateur
            }
        }
        return false;
    }
}