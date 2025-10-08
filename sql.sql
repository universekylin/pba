-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: pba-mysqlserver.c7uuwscka6bv.ap-southeast-2.rds.amazonaws.com    Database: pba
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `divisions`
--

DROP TABLE IF EXISTS `divisions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `divisions` (
  `id` tinyint unsigned NOT NULL,
  `code` varchar(16) NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `divisions`
--

LOCK TABLES `divisions` WRITE;
/*!40000 ALTER TABLE `divisions` DISABLE KEYS */;
INSERT INTO `divisions` VALUES (1,'champion','Champion'),(2,'d1','Division 1'),(3,'d2','Division 2');
/*!40000 ALTER TABLE `divisions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `match_player_stats`
--

DROP TABLE IF EXISTS `match_player_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_player_stats` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `match_id` int unsigned NOT NULL,
  `player_id` int unsigned NOT NULL,
  `team_id` int unsigned NOT NULL,
  `points` int NOT NULL DEFAULT '0',
  `rebounds` int NOT NULL DEFAULT '0',
  `steals` int NOT NULL DEFAULT '0',
  `assists` int NOT NULL DEFAULT '0',
  `blocks` int NOT NULL DEFAULT '0',
  `one_pt_made` smallint unsigned NOT NULL DEFAULT '0',
  `two_pt_made` smallint unsigned NOT NULL DEFAULT '0',
  `three_pt_made` smallint unsigned NOT NULL DEFAULT '0',
  `fouls` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_match_player` (`match_id`,`player_id`),
  KEY `player_id` (`player_id`),
  KEY `team_id` (`team_id`),
  CONSTRAINT `match_player_stats_ibfk_1` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`) ON DELETE CASCADE,
  CONSTRAINT `match_player_stats_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `match_player_stats_ibfk_3` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `match_player_stats`
--

LOCK TABLES `match_player_stats` WRITE;
/*!40000 ALTER TABLE `match_player_stats` DISABLE KEYS */;
INSERT INTO `match_player_stats` VALUES (42,311,16,17,9,0,0,0,0,0,0,3,0),(43,245,15,17,27,1,2,3,10,0,0,9,0),(44,245,16,17,18,10,1,2,3,0,0,6,0),(45,245,13,20,8,0,0,0,0,0,4,0,0),(46,245,14,20,12,0,0,0,0,0,6,0,0),(55,267,6,2,21,0,0,0,0,0,0,7,0),(56,267,12,16,12,0,0,0,0,0,0,4,3),(57,267,8,16,9,0,0,0,0,0,0,3,4),(58,267,11,16,6,0,0,0,0,0,0,2,0),(59,267,1,2,3,0,0,0,0,0,0,1,0),(60,289,19,21,15,0,0,0,0,0,0,5,0),(61,289,21,24,10,0,0,0,0,0,5,0,0);
/*!40000 ALTER TABLE `match_player_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `season_id` int unsigned NOT NULL,
  `division_id` tinyint unsigned NOT NULL,
  `stage` enum('regular','playoff') NOT NULL DEFAULT 'regular',
  `round_no` int unsigned DEFAULT NULL,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `venue` varchar(120) DEFAULT NULL,
  `status` enum('scheduled','live','finished','canceled') NOT NULL DEFAULT 'scheduled',
  `home_team_id` int unsigned DEFAULT NULL,
  `away_team_id` int unsigned DEFAULT NULL,
  `home_score` int DEFAULT NULL,
  `away_score` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_match_once` (`season_id`,`division_id`,`stage`,`round_no`,`home_team_id`,`away_team_id`),
  KEY `fk_match_division` (`division_id`),
  KEY `fk_match_home` (`home_team_id`),
  KEY `fk_match_away` (`away_team_id`),
  KEY `idx_match_home_bucket` (`season_id`,`division_id`,`round_no`,`home_team_id`),
  KEY `idx_match_away_bucket` (`season_id`,`division_id`,`round_no`,`away_team_id`),
  KEY `idx_match_bucket` (`season_id`,`division_id`,`stage`,`round_no`),
  CONSTRAINT `fk_match_away` FOREIGN KEY (`away_team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_match_division` FOREIGN KEY (`division_id`) REFERENCES `divisions` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_match_home` FOREIGN KEY (`home_team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_match_season` FOREIGN KEY (`season_id`) REFERENCES `seasons` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_not_same` CHECK (((`home_team_id` is null) or (`away_team_id` is null) or (`home_team_id` <> `away_team_id`)))
) ENGINE=InnoDB AUTO_INCREMENT=312 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matches`
--

LOCK TABLES `matches` WRITE;
/*!40000 ALTER TABLE `matches` DISABLE KEYS */;
INSERT INTO `matches` VALUES (245,1,1,'regular',1,NULL,NULL,NULL,'scheduled',17,20,45,20,'2025-09-30 15:50:45','2025-10-02 09:52:01'),(246,1,1,'regular',1,NULL,NULL,NULL,'scheduled',18,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(247,1,1,'regular',2,NULL,NULL,NULL,'scheduled',19,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(248,1,1,'regular',2,NULL,NULL,NULL,'scheduled',18,20,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(249,1,1,'regular',3,NULL,NULL,NULL,'scheduled',17,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(250,1,1,'regular',3,NULL,NULL,NULL,'scheduled',19,20,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(251,1,1,'regular',4,NULL,NULL,NULL,'scheduled',20,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(252,1,1,'regular',4,NULL,NULL,NULL,'scheduled',19,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(253,1,1,'regular',5,NULL,NULL,NULL,'scheduled',17,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(254,1,1,'regular',5,NULL,NULL,NULL,'scheduled',20,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(255,1,1,'regular',6,NULL,NULL,NULL,'scheduled',18,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(256,1,1,'regular',6,NULL,NULL,NULL,'scheduled',20,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(257,1,1,'regular',7,NULL,NULL,NULL,'scheduled',20,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(258,1,1,'regular',7,NULL,NULL,NULL,'scheduled',19,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(259,1,1,'regular',8,NULL,NULL,NULL,'scheduled',17,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(260,1,1,'regular',8,NULL,NULL,NULL,'scheduled',20,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(261,1,1,'regular',9,NULL,NULL,NULL,'scheduled',18,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(262,1,1,'regular',9,NULL,NULL,NULL,'scheduled',20,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(263,1,1,'regular',10,NULL,NULL,NULL,'scheduled',20,17,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(264,1,1,'regular',10,NULL,NULL,NULL,'scheduled',19,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(265,1,1,'regular',11,NULL,NULL,NULL,'scheduled',17,19,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(266,1,1,'regular',11,NULL,NULL,NULL,'scheduled',20,18,NULL,NULL,'2025-09-30 15:50:45','2025-09-30 15:50:45'),(267,1,2,'regular',1,NULL,NULL,NULL,'scheduled',2,16,24,27,'2025-09-30 15:50:54','2025-09-30 19:26:21'),(268,1,2,'regular',1,NULL,NULL,NULL,'scheduled',4,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(269,1,2,'regular',2,NULL,NULL,NULL,'scheduled',5,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(270,1,2,'regular',2,NULL,NULL,NULL,'scheduled',4,16,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(271,1,2,'regular',3,NULL,NULL,NULL,'scheduled',2,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(272,1,2,'regular',3,NULL,NULL,NULL,'scheduled',5,16,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(273,1,2,'regular',4,NULL,NULL,NULL,'scheduled',16,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(274,1,2,'regular',4,NULL,NULL,NULL,'scheduled',5,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(275,1,2,'regular',5,NULL,NULL,NULL,'scheduled',2,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(276,1,2,'regular',5,NULL,NULL,NULL,'scheduled',16,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(277,1,2,'regular',6,NULL,NULL,NULL,'scheduled',4,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(278,1,2,'regular',6,NULL,NULL,NULL,'scheduled',16,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(279,1,2,'regular',7,NULL,NULL,NULL,'scheduled',16,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(280,1,2,'regular',7,NULL,NULL,NULL,'scheduled',5,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(281,1,2,'regular',8,NULL,NULL,NULL,'scheduled',2,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(282,1,2,'regular',8,NULL,NULL,NULL,'scheduled',16,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(283,1,2,'regular',9,NULL,NULL,NULL,'scheduled',4,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(284,1,2,'regular',9,NULL,NULL,NULL,'scheduled',16,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(285,1,2,'regular',10,NULL,NULL,NULL,'scheduled',16,2,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(286,1,2,'regular',10,NULL,NULL,NULL,'scheduled',5,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(287,1,2,'regular',11,NULL,NULL,NULL,'scheduled',2,5,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(288,1,2,'regular',11,NULL,NULL,NULL,'scheduled',16,4,NULL,NULL,'2025-09-30 15:50:54','2025-09-30 15:50:54'),(289,1,3,'regular',1,NULL,NULL,NULL,'scheduled',21,24,15,10,'2025-09-30 15:51:01','2025-09-30 19:43:31'),(290,1,3,'regular',1,NULL,NULL,NULL,'scheduled',22,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(291,1,3,'regular',2,NULL,NULL,NULL,'scheduled',23,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(292,1,3,'regular',2,NULL,NULL,NULL,'scheduled',22,24,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(293,1,3,'regular',3,NULL,NULL,NULL,'scheduled',21,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(294,1,3,'regular',3,NULL,NULL,NULL,'scheduled',23,24,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(295,1,3,'regular',4,NULL,NULL,NULL,'scheduled',24,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(296,1,3,'regular',4,NULL,NULL,NULL,'scheduled',23,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(297,1,3,'regular',5,NULL,NULL,NULL,'scheduled',21,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(298,1,3,'regular',5,NULL,NULL,NULL,'scheduled',24,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(299,1,3,'regular',6,NULL,NULL,NULL,'scheduled',22,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(300,1,3,'regular',6,NULL,NULL,NULL,'scheduled',24,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(301,1,3,'regular',7,NULL,NULL,NULL,'scheduled',24,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(302,1,3,'regular',7,NULL,NULL,NULL,'scheduled',23,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(303,1,3,'regular',8,NULL,NULL,NULL,'scheduled',21,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(304,1,3,'regular',8,NULL,NULL,NULL,'scheduled',24,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(305,1,3,'regular',9,NULL,NULL,NULL,'scheduled',22,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(306,1,3,'regular',9,NULL,NULL,NULL,'scheduled',24,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(307,1,3,'regular',10,NULL,NULL,NULL,'scheduled',24,21,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(308,1,3,'regular',10,NULL,NULL,NULL,'scheduled',23,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(309,1,3,'regular',11,NULL,NULL,NULL,'scheduled',21,23,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(310,1,3,'regular',11,NULL,NULL,NULL,'scheduled',24,22,NULL,NULL,'2025-09-30 15:51:01','2025-09-30 15:51:01'),(311,1,1,'playoff',1,'2025-09-30','18:30:00','Court 7','scheduled',17,18,9,0,'2025-09-30 16:03:56','2025-09-30 16:18:29');
/*!40000 ALTER TABLE `matches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_match_stats`
--

DROP TABLE IF EXISTS `player_match_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_match_stats` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `match_id` int unsigned NOT NULL,
  `player_id` int unsigned NOT NULL,
  `team_id` int unsigned NOT NULL,
  `points` smallint unsigned NOT NULL DEFAULT '0',
  `rebounds` smallint unsigned NOT NULL DEFAULT '0',
  `steals` smallint unsigned NOT NULL DEFAULT '0',
  `assists` smallint unsigned NOT NULL DEFAULT '0',
  `blocks` smallint unsigned NOT NULL DEFAULT '0',
  `fouls` smallint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_player_once` (`match_id`,`player_id`),
  KEY `idx_pms_match` (`match_id`),
  KEY `idx_pms_team` (`match_id`,`team_id`),
  KEY `fk_pms_player` (`player_id`),
  KEY `fk_pms_team` (`team_id`),
  CONSTRAINT `fk_pms_match` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pms_player` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pms_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_match_stats`
--

LOCK TABLES `player_match_stats` WRITE;
/*!40000 ALTER TABLE `player_match_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `player_match_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `players` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `team_id` int unsigned NOT NULL,
  `name` varchar(120) NOT NULL,
  `number` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_players_team` (`team_id`),
  CONSTRAINT `fk_players_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `players`
--

LOCK TABLES `players` WRITE;
/*!40000 ALTER TABLE `players` DISABLE KEYS */;
INSERT INTO `players` VALUES (1,2,'麒麟',7),(6,2,'tony',2),(8,16,'队长',2),(9,4,'麒麟',7),(10,4,'老戴',33),(11,16,'Xu',88),(12,16,'shu',13),(13,20,'nelson',17),(14,20,'harry',22),(15,17,'wade',30),(16,17,'joe',14),(17,18,'danny',2),(18,19,'song',4),(19,21,'justin',21),(20,22,'bob',2),(21,24,'tian',3),(22,4,'shu',12);
/*!40000 ALTER TABLE `players` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seasons`
--

DROP TABLE IF EXISTS `seasons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seasons` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seasons`
--

LOCK TABLES `seasons` WRITE;
/*!40000 ALTER TABLE `seasons` DISABLE KEYS */;
INSERT INTO `seasons` VALUES (1,'2025-S8','Season 8 (2025)');
/*!40000 ALTER TABLE `seasons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team_season_division`
--

DROP TABLE IF EXISTS `team_season_division`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team_season_division` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `season_id` int unsigned NOT NULL,
  `division_id` tinyint unsigned NOT NULL,
  `team_id` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_team_in_season` (`season_id`,`team_id`),
  KEY `idx_bucket` (`season_id`,`division_id`),
  KEY `fk_tsd_division` (`division_id`),
  KEY `fk_tsd_team` (`team_id`),
  CONSTRAINT `fk_tsd_division` FOREIGN KEY (`division_id`) REFERENCES `divisions` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_tsd_season` FOREIGN KEY (`season_id`) REFERENCES `seasons` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tsd_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team_season_division`
--

LOCK TABLES `team_season_division` WRITE;
/*!40000 ALTER TABLE `team_season_division` DISABLE KEYS */;
INSERT INTO `team_season_division` VALUES (2,1,2,2),(4,1,2,4),(5,1,2,5),(16,1,2,16),(21,1,1,17),(22,1,1,18),(23,1,1,19),(24,1,1,20),(25,1,3,21),(26,1,3,22),(27,1,3,23),(30,1,3,24);
/*!40000 ALTER TABLE `team_season_division` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `logo_url` varchar(255) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_team_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teams`
--

LOCK TABLES `teams` WRITE;
/*!40000 ALTER TABLE `teams` DISABLE KEYS */;
INSERT INTO `teams` VALUES (2,'我很帅',NULL,NULL,'2025-09-18 05:18:02','2025-09-18 13:08:07'),(4,'1',NULL,NULL,'2025-09-18 06:22:27','2025-09-18 06:22:27'),(5,'2',NULL,NULL,'2025-09-18 06:22:30','2025-09-18 06:22:30'),(16,'13','/static/team-logos/pba2_1.png',NULL,'2025-09-18 13:06:18','2025-09-18 13:06:18'),(17,'c1','/static/team-logos/pbalogo.jpg',NULL,'2025-09-21 05:01:27','2025-10-03 15:04:53'),(18,'c2',NULL,NULL,'2025-09-21 05:01:27','2025-09-21 05:01:27'),(19,'c3',NULL,NULL,'2025-09-21 05:01:27','2025-09-21 05:01:27'),(20,'c4','/static/team-logos/pba2_2.png',NULL,'2025-09-21 05:01:27','2025-09-24 07:01:15'),(21,'d1',NULL,NULL,'2025-09-21 05:01:28','2025-09-24 09:19:21'),(22,'d2',NULL,NULL,'2025-09-21 05:01:28','2025-09-24 09:19:21'),(23,'d3',NULL,NULL,'2025-09-21 05:01:28','2025-09-24 09:19:21'),(24,'d4',NULL,NULL,'2025-09-24 09:19:21','2025-09-24 09:19:21');
/*!40000 ALTER TABLE `teams` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-04  1:08:44
