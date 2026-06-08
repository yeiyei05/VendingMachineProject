<?php
echo "--- DOSSIERS TROUVÉS À LA RACINE ---<br>";
$folders = glob('C:\xampp\htdocs\*');
foreach($folders as $f) {
    echo $f . "<br>";
}