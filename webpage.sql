-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3307
-- Tiempo de generación: 04-10-2024 a las 14:39:19
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `webpage`
--

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `notfinishedjob`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `notfinishedjob` (
`tjob_idjob` int(11)
,`start` datetime
,`end` datetime
,`finished` tinyint(1)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbuilding`
--

CREATE TABLE `tbuilding` (
  `IdBuilding` int(11) NOT NULL,
  `Comprobante` varchar(1000) NOT NULL,
  `ZIP` varchar(50) NOT NULL,
  `Direction` varchar(100) NOT NULL,
  `Active` tinyint(1) NOT NULL,
  `TUserOther_IdOther` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `tbuildingactive`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `tbuildingactive` (
`idbuilding` int(11)
,`direction` varchar(100)
,`zip` varchar(50)
,`active` tinyint(1)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tbuldingreport`
--

CREATE TABLE `tbuldingreport` (
  `IdReport` int(11) NOT NULL,
  `IdBuilding` int(11) NOT NULL,
  `IdStudent` int(11) NOT NULL,
  `Description` varchar(500) NOT NULL,
  `Created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `tbuldingzip`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `tbuldingzip` (
`IdBuilding` int(11)
,`Direction` varchar(100)
,`ZIP` varchar(50)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tcompletedjob`
--

CREATE TABLE `tcompletedjob` (
  `Start` datetime NOT NULL,
  `End` datetime NOT NULL,
  `Finished` tinyint(1) NOT NULL,
  `TUserStudent_IdStudent` int(11) NOT NULL,
  `TUserOther_IdOther` int(11) NOT NULL,
  `TJob_IdJob` int(11) NOT NULL,
  `Active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tjob`
--

CREATE TABLE `tjob` (
  `IdJob` int(11) NOT NULL,
  `JobDescription` varchar(100) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  `Active` tinyint(1) NOT NULL,
  `TUserOther_IdOther` int(11) NOT NULL,
  `IdBuilding` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tjobreport`
--

CREATE TABLE `tjobreport` (
  `IdReport` int(11) NOT NULL,
  `IdJob` int(11) NOT NULL,
  `IdStudent` int(11) NOT NULL,
  `Created_At` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Description` varchar(500) NOT NULL,
  `active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tmessage`
--

CREATE TABLE `tmessage` (
  `IdMessage` int(11) NOT NULL,
  `MessageDescription` varchar(5000) NOT NULL,
  `DateMessage` datetime NOT NULL,
  `Active` tinyint(1) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  `ReceivedAt` datetime NOT NULL,
  `ReadedAt` datetime NOT NULL,
  `TUserStudent_IdStudent` int(11) NOT NULL,
  `TUserOther_IdOther` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tmessagereport`
--

CREATE TABLE `tmessagereport` (
  `IdReport` int(11) NOT NULL,
  `IdMessage` int(11) NOT NULL,
  `IdStudent` int(11) NOT NULL,
  `IdOther` int(11) NOT NULL,
  `Created_At` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Description` varchar(500) NOT NULL,
  `Active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `totherreport`
--

CREATE TABLE `totherreport` (
  `IdReport` int(11) NOT NULL,
  `IdStudent` int(11) NOT NULL,
  `IdOther` int(11) NOT NULL,
  `Created_At` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Description` varchar(500) NOT NULL,
  `Active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tstudentreport`
--

CREATE TABLE `tstudentreport` (
  `IdReport` int(11) NOT NULL,
  `IdStuent` int(11) NOT NULL,
  `IdOther` int(11) NOT NULL,
  `Created_At` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Description` varchar(500) NOT NULL,
  `Active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tuserother`
--

CREATE TABLE `tuserother` (
  `IdOther` int(11) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `Age` varchar(3) NOT NULL,
  `Mail` varchar(50) NOT NULL,
  `Phone` varchar(50) NOT NULL,
  `INE` varchar(1000) DEFAULT NULL,
  `Active` tinyint(1) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  `OtherCalification` tinyint(1) NOT NULL,
  `Password` varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `tuserotheradult`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `tuserotheradult` (
`idstudent` int(11)
,`name` varchar(50)
,`lastname` varchar(50)
,`age` varchar(3)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tuserstudent`
--

CREATE TABLE `tuserstudent` (
  `IdStudent` int(11) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `Age` varchar(3) NOT NULL,
  `Mail` varchar(50) NOT NULL,
  `Phone` varchar(50) NOT NULL,
  `INE` varchar(1000) DEFAULT NULL,
  `SchoolID` varchar(1000) NOT NULL,
  `Active` tinyint(1) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  `Calification` tinyint(1) NOT NULL,
  `Password` varchar(25) NOT NULL,
  `CURP` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `tuserstudentadult`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `tuserstudentadult` (
`idstudent` int(11)
,`name` varchar(50)
,`lastname` varchar(50)
,`age` varchar(3)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `notfinishedjob`
--
DROP TABLE IF EXISTS `notfinishedjob`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `notfinishedjob`  AS SELECT `tcompletedjob`.`TJob_IdJob` AS `tjob_idjob`, `tcompletedjob`.`Start` AS `start`, `tcompletedjob`.`End` AS `end`, `tcompletedjob`.`Finished` AS `finished` FROM `tcompletedjob` WHERE `tcompletedjob`.`Finished` = 0 ;

-- --------------------------------------------------------

--
-- Estructura para la vista `tbuildingactive`
--
DROP TABLE IF EXISTS `tbuildingactive`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbuildingactive`  AS SELECT `tbuilding`.`IdBuilding` AS `idbuilding`, `tbuilding`.`Direction` AS `direction`, `tbuilding`.`ZIP` AS `zip`, `tbuilding`.`Active` AS `active` FROM `tbuilding` WHERE `tbuilding`.`Active` = 1 ;

-- --------------------------------------------------------

--
-- Estructura para la vista `tbuldingzip`
--
DROP TABLE IF EXISTS `tbuldingzip`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbuldingzip`  AS SELECT `tbuilding`.`IdBuilding` AS `IdBuilding`, `tbuilding`.`Direction` AS `Direction`, `tbuilding`.`ZIP` AS `ZIP` FROM `tbuilding` WHERE `tbuilding`.`ZIP` = '31050' ;

-- --------------------------------------------------------

--
-- Estructura para la vista `tuserotheradult`
--
DROP TABLE IF EXISTS `tuserotheradult`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tuserotheradult`  AS SELECT `tuserstudent`.`IdStudent` AS `idstudent`, `tuserstudent`.`Name` AS `name`, `tuserstudent`.`LastName` AS `lastname`, `tuserstudent`.`Age` AS `age` FROM `tuserstudent` WHERE `tuserstudent`.`Age` >= 18 ;

-- --------------------------------------------------------

--
-- Estructura para la vista `tuserstudentadult`
--
DROP TABLE IF EXISTS `tuserstudentadult`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tuserstudentadult`  AS SELECT `tuserstudent`.`IdStudent` AS `idstudent`, `tuserstudent`.`Name` AS `name`, `tuserstudent`.`LastName` AS `lastname`, `tuserstudent`.`Age` AS `age` FROM `tuserstudent` WHERE `tuserstudent`.`Age` >= 18 ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `tbuilding`
--
ALTER TABLE `tbuilding`
  ADD PRIMARY KEY (`IdBuilding`);

--
-- Indices de la tabla `tbuldingreport`
--
ALTER TABLE `tbuldingreport`
  ADD PRIMARY KEY (`IdReport`);

--
-- Indices de la tabla `tjob`
--
ALTER TABLE `tjob`
  ADD PRIMARY KEY (`IdJob`);

--
-- Indices de la tabla `tjobreport`
--
ALTER TABLE `tjobreport`
  ADD PRIMARY KEY (`IdReport`);
ALTER TABLE `tjobreport` ADD FULLTEXT KEY `JobReportDescription` (`Description`);

--
-- Indices de la tabla `tmessage`
--
ALTER TABLE `tmessage`
  ADD PRIMARY KEY (`IdMessage`);

--
-- Indices de la tabla `tmessagereport`
--
ALTER TABLE `tmessagereport`
  ADD PRIMARY KEY (`IdReport`);

--
-- Indices de la tabla `totherreport`
--
ALTER TABLE `totherreport`
  ADD PRIMARY KEY (`IdReport`);

--
-- Indices de la tabla `tuserother`
--
ALTER TABLE `tuserother`
  ADD PRIMARY KEY (`IdOther`),
  ADD UNIQUE KEY `UserOtherMail` (`Mail`),
  ADD KEY `OtherName` (`Name`);

--
-- Indices de la tabla `tuserstudent`
--
ALTER TABLE `tuserstudent`
  ADD PRIMARY KEY (`IdStudent`),
  ADD UNIQUE KEY `StudentPhone` (`Phone`),
  ADD UNIQUE KEY `StudentCURP` (`CURP`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `tbuilding`
--
ALTER TABLE `tbuilding`
  MODIFY `IdBuilding` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tbuldingreport`
--
ALTER TABLE `tbuldingreport`
  MODIFY `IdReport` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tjob`
--
ALTER TABLE `tjob`
  MODIFY `IdJob` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tjobreport`
--
ALTER TABLE `tjobreport`
  MODIFY `IdReport` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tmessage`
--
ALTER TABLE `tmessage`
  MODIFY `IdMessage` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tmessagereport`
--
ALTER TABLE `tmessagereport`
  MODIFY `IdReport` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `totherreport`
--
ALTER TABLE `totherreport`
  MODIFY `IdReport` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tuserother`
--
ALTER TABLE `tuserother`
  MODIFY `IdOther` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tuserstudent`
--
ALTER TABLE `tuserstudent`
  MODIFY `IdStudent` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
