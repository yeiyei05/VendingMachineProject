-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mer. 10 juin 2026 à 15:57
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `vending_machine_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `devices`
--

CREATE TABLE `devices` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` enum('sensor','actuator') NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `devices`
--

INSERT INTO `devices` (`id`, `name`, `type`, `location`, `created_at`) VALUES
(1, 'HC-SR04', 'sensor', 'Distributeur A', '2026-06-10 08:37:37');

-- --------------------------------------------------------

--
-- Structure de la table `device_history`
--

CREATE TABLE `device_history` (
  `id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `value_recorded` varchar(100) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `device_history`
--

INSERT INTO `device_history` (`id`, `device_id`, `value_recorded`, `timestamp`) VALUES
(1071, 1, '4', '2026-06-10 09:32:46'),
(1072, 1, '3', '2026-06-10 09:32:47'),
(1073, 1, '3', '2026-06-10 09:32:47'),
(1074, 1, '4', '2026-06-10 09:32:48'),
(1075, 1, '4', '2026-06-10 09:32:48'),
(1076, 1, '4', '2026-06-10 09:32:49'),
(1077, 1, '3', '2026-06-10 09:32:49'),
(1078, 1, '3', '2026-06-10 09:32:50'),
(1079, 1, '4', '2026-06-10 09:32:51'),
(1080, 1, '3', '2026-06-10 09:32:51'),
(1081, 1, '3', '2026-06-10 09:32:52'),
(1082, 1, '3', '2026-06-10 09:32:52'),
(1083, 1, '3', '2026-06-10 09:32:53'),
(1084, 1, '3', '2026-06-10 09:32:53'),
(1085, 1, '3', '2026-06-10 09:32:54'),
(1086, 1, '3', '2026-06-10 09:32:54'),
(1087, 1, '3', '2026-06-10 09:32:55'),
(1088, 1, '4', '2026-06-10 09:32:55'),
(1089, 1, '5', '2026-06-10 09:32:56'),
(1090, 1, '5', '2026-06-10 09:32:56'),
(1091, 1, '5', '2026-06-10 09:32:57'),
(1092, 1, '5', '2026-06-10 09:32:57'),
(1093, 1, '4', '2026-06-10 09:32:58'),
(1094, 1, '5', '2026-06-10 09:32:58'),
(1095, 1, '4', '2026-06-10 09:32:59'),
(1096, 1, '4', '2026-06-10 09:32:59'),
(1097, 1, '5', '2026-06-10 09:33:00'),
(1098, 1, '4', '2026-06-10 09:33:00'),
(1099, 1, '4', '2026-06-10 09:33:01'),
(1100, 1, '4', '2026-06-10 09:33:01'),
(1101, 1, '4', '2026-06-10 09:33:02'),
(1102, 1, '5', '2026-06-10 09:33:02'),
(1103, 1, '5', '2026-06-10 09:33:03'),
(1104, 1, '5', '2026-06-10 09:33:03'),
(1105, 1, '5', '2026-06-10 09:33:04'),
(1106, 1, '4', '2026-06-10 09:33:04'),
(1107, 1, '4', '2026-06-10 09:33:05'),
(1108, 1, '4', '2026-06-10 09:33:05'),
(1109, 1, '4', '2026-06-10 09:33:06'),
(1110, 1, '4', '2026-06-10 09:33:06'),
(1111, 1, '4', '2026-06-10 09:33:07'),
(1112, 1, '4', '2026-06-10 09:33:07'),
(1113, 1, '4', '2026-06-10 09:33:08'),
(1114, 1, '4', '2026-06-10 09:33:08'),
(1115, 1, '0', '2026-06-10 09:33:12'),
(1116, 1, '0', '2026-06-10 09:33:13'),
(1117, 1, '5', '2026-06-10 09:33:14'),
(1118, 1, '5', '2026-06-10 09:33:14'),
(1119, 1, '5', '2026-06-10 09:33:15'),
(1120, 1, '5', '2026-06-10 09:33:15'),
(1121, 1, '5', '2026-06-10 09:33:16'),
(1122, 1, '5', '2026-06-10 09:33:16'),
(1123, 1, '5', '2026-06-10 09:33:17'),
(1124, 1, '5', '2026-06-10 09:33:17'),
(1125, 1, '5', '2026-06-10 09:33:18'),
(1126, 1, '5', '2026-06-10 09:33:18'),
(1127, 1, '5', '2026-06-10 09:33:19'),
(1128, 1, '5', '2026-06-10 09:33:19'),
(1129, 1, '5', '2026-06-10 09:33:20'),
(1130, 1, '5', '2026-06-10 09:33:20'),
(1131, 1, '5', '2026-06-10 09:33:21'),
(1132, 1, '5', '2026-06-10 09:33:21'),
(1133, 1, '3', '2026-06-10 09:33:22'),
(1134, 1, '3', '2026-06-10 09:33:22'),
(1135, 1, '3', '2026-06-10 09:33:23'),
(1136, 1, '3', '2026-06-10 09:33:23'),
(1137, 1, '3', '2026-06-10 09:33:24'),
(1138, 1, '3', '2026-06-10 09:33:24'),
(1139, 1, '3', '2026-06-10 09:33:25'),
(1140, 1, '3', '2026-06-10 09:33:25'),
(1141, 1, '3', '2026-06-10 09:33:26'),
(1142, 1, '3', '2026-06-10 09:33:27'),
(1143, 1, '3', '2026-06-10 09:33:27'),
(1144, 1, '3', '2026-06-10 09:33:28'),
(1145, 1, '3', '2026-06-10 09:33:28'),
(1146, 1, '3', '2026-06-10 09:33:29'),
(1147, 1, '3', '2026-06-10 09:33:29'),
(1148, 1, '3', '2026-06-10 09:33:30'),
(1149, 1, '3', '2026-06-10 09:33:30'),
(1150, 1, '2', '2026-06-10 09:33:31'),
(1151, 1, '2', '2026-06-10 09:33:31'),
(1152, 1, '2', '2026-06-10 09:33:32'),
(1153, 1, '2', '2026-06-10 09:33:32'),
(1154, 1, '2', '2026-06-10 09:33:33'),
(1155, 1, '2', '2026-06-10 09:33:33'),
(1156, 1, '2', '2026-06-10 09:33:34'),
(1157, 1, '2', '2026-06-10 09:33:34'),
(1158, 1, '2', '2026-06-10 09:33:35'),
(1159, 1, '2', '2026-06-10 09:33:35'),
(1160, 1, '2', '2026-06-10 09:33:36'),
(1161, 1, '2', '2026-06-10 09:33:36'),
(1162, 1, '2', '2026-06-10 09:33:37'),
(1163, 1, '1', '2026-06-10 09:33:37'),
(1164, 1, '1', '2026-06-10 09:33:38'),
(1165, 1, '1', '2026-06-10 09:33:38'),
(1166, 1, '1', '2026-06-10 09:33:39'),
(1167, 1, '1', '2026-06-10 09:33:39'),
(1168, 1, '1', '2026-06-10 09:33:40'),
(1169, 1, '1', '2026-06-10 09:33:40'),
(1170, 1, '1', '2026-06-10 09:33:41'),
(1171, 1, '1', '2026-06-10 09:33:42'),
(1172, 1, '1', '2026-06-10 09:33:42'),
(1173, 1, '1', '2026-06-10 09:33:43'),
(1174, 1, '1', '2026-06-10 09:33:43'),
(1175, 1, '1', '2026-06-10 09:33:44'),
(1176, 1, '1', '2026-06-10 09:33:44'),
(1177, 1, '1', '2026-06-10 09:33:45'),
(1178, 1, '1', '2026-06-10 09:33:45'),
(1179, 1, '0', '2026-06-10 09:33:46'),
(1180, 1, '0', '2026-06-10 09:33:46'),
(1181, 1, '0', '2026-06-10 09:33:48'),
(1182, 1, '0', '2026-06-10 09:33:49'),
(1183, 1, '0', '2026-06-10 09:33:52'),
(1184, 1, '0', '2026-06-10 09:33:53'),
(1185, 1, '0', '2026-06-10 09:34:01'),
(1186, 1, '1', '2026-06-10 09:34:02'),
(1187, 1, '0', '2026-06-10 09:34:02'),
(1188, 1, '0', '2026-06-10 09:34:03'),
(1189, 1, '5', '2026-06-10 13:13:47'),
(1190, 1, '5', '2026-06-10 13:41:08');

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `created_at`) VALUES
(5, 'pha', 'rellpha0@gmail.com', '$2y$10$VbMU1aEjCnUZLIy/Ujf6HeJQQl9TmuftqSdpYbaRpDJSnUlhy8eQ6', '2026-06-10 13:30:34'),
(6, 'test1', 'test1@test1.fr', '$2y$10$mds31CCAW.oPE7fEdEKfC.kI4PU5yK8xO71WsjUTNosxaO2ddMWuK', '2026-06-10 13:36:19');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `device_history`
--
ALTER TABLE `device_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `device_id` (`device_id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `devices`
--
ALTER TABLE `devices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `device_history`
--
ALTER TABLE `device_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1191;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `device_history`
--
ALTER TABLE `device_history`
  ADD CONSTRAINT `device_history_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
