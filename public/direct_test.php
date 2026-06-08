<?php
// public/direct_test.php

error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h3>Vérification des accès physiques :</h3>";

// Test d'existence direct
$file1 = __DIR__ . '/../config/database.php';
$file2 = 'C:\\xampp\\htdocs\\Projet_Vending_Machine\\config\\database.php';

echo "Chemin relatif calculé : " . $file1 . "<br>";
echo "Le fichier existe-t-il en relatif ? " . (file_exists($file1) ? '✅ OUI' : '❌ NON') . "<br><br>";

echo "Chemin absolu calculé : " . $file2 . "<br>";
echo "Le fichier existe-t-il en absolu ? " . (file_exists($file2) ? '✅ OUI' : '❌ NON') . "<br><br>";

if (file_exists($file1)) {
    echo "Tentative d'inclusion...<br>";
    include_once $file1;
    if (class_exists('Database')) {
        echo "✅ Succès ! La classe Database est chargée et visible !";
    } else {
        echo "❌ Fichier inclus, mais classe introuvable.";
    }
}
