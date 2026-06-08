<?php

namespace controllers;
use models\User;

require_once '../models/User.php';

class AuthController
{
    private $userModel;

    public function __construct($db)
    {
        $this->userModel = new User($db);
    }

    public function handleLogin()
    {
        $error = null;
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $username = $_POST['username'] ?? '';
            $password = $_POST['password'] ?? '';

            $user = $this->userModel->login($username, $password);
            if ($user) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                header('Location: index.php?page=dashboard');
                exit();
            } else {
                $error = "Identifiants invalides ou clé de sécurité incorrecte.";
            }
        }
        include __DIR__ . '/../views/auth/login.php';
    }

    public function handleRegister()
    {
        $error = null;
        $success = null;
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $username = $_POST['username'] ?? '';
            $email = $_POST['email'] ?? '';
            $password = $_POST['password'] ?? '';

            if ($this->userModel->register($username, $email, $password)) {
                $success = "Compte créé ! Vous pouvez vous connecter.";
            } else {
                $error = "Erreur lors de la création du compte.";
            }
        }
        include __DIR__ . '/../views/auth/register.php';
    }

    public function logout()
    {
        session_destroy();
        header('Location: index.php?page=home');
        exit();
    }
}