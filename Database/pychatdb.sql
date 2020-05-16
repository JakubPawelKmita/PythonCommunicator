-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Czas generowania: 16 Maj 2020, 14:34
-- Wersja serwera: 10.1.28-MariaDB
-- Wersja PHP: 7.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Baza danych: `pychatdb`
--
CREATE DATABASE IF NOT EXISTS `pychatdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `pychatdb`;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `chatmember`
--

DROP TABLE IF EXISTS `chatmember`;
CREATE TABLE `chatmember` (
  `id` int(11) NOT NULL,
  `chat` int(11) NOT NULL,
  `user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Zrzut danych tabeli `chatmember`
--

INSERT INTO `chatmember` (`id`, `chat`, `user`) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 2, 1),
(4, 2, 2),
(5, 2, 3);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `chats`
--

DROP TABLE IF EXISTS `chats`;
CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `creator` int(11) NOT NULL,
  `creationtime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Zrzut danych tabeli `chats`
--

INSERT INTO `chats` (`id`, `creator`, `creationtime`) VALUES
(1, 1, '2020-05-15 19:01:04'),
(2, 1, '2020-05-15 19:01:15');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `messages`
--

DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `user` int(11) NOT NULL,
  `chat` int(11) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `msg` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Zrzut danych tabeli `messages`
--

INSERT INTO `messages` (`id`, `user`, `chat`, `time`, `msg`) VALUES
(1, 1, 1, '2020-05-15 19:19:02', 'msg1'),
(2, 2, 1, '2020-05-15 19:19:35', 'msg2'),
(3, 1, 1, '2020-05-15 19:19:54', 'msg3'),
(4, 2, 1, '2020-05-15 19:20:10', 'msg4'),
(5, 1, 2, '2020-05-15 19:20:43', 'msg1'),
(6, 2, 2, '2020-05-15 19:20:58', 'msg2'),
(7, 3, 2, '2020-05-15 19:21:21', 'msg3');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `login` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `email` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Zrzut danych tabeli `users`
--

INSERT INTO `users` (`id`, `login`, `password`, `email`) VALUES
(1, 'a', 'a', 'a'),
(2, 'b', 'b', 'b'),
(3, 'c', 'c', 'c');

--
-- Indeksy dla zrzutów tabel
--

--
-- Indexes for table `chatmember`
--
ALTER TABLE `chatmember`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat` (`chat`),
  ADD KEY `user` (`user`);

--
-- Indexes for table `chats`
--
ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`),
  ADD KEY `creator` (`creator`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user` (`user`),
  ADD KEY `chat` (`chat`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT dla tabeli `chatmember`
--
ALTER TABLE `chatmember`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT dla tabeli `chats`
--
ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT dla tabeli `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT dla tabeli `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Ograniczenia dla zrzutów tabel
--

--
-- Ograniczenia dla tabeli `chatmember`
--
ALTER TABLE `chatmember`
  ADD CONSTRAINT `chatmember_ibfk_1` FOREIGN KEY (`chat`) REFERENCES `chats` (`id`),
  ADD CONSTRAINT `chatmember_ibfk_2` FOREIGN KEY (`user`) REFERENCES `users` (`id`);

--
-- Ograniczenia dla tabeli `chats`
--
ALTER TABLE `chats`
  ADD CONSTRAINT `chats_ibfk_1` FOREIGN KEY (`creator`) REFERENCES `users` (`id`);

--
-- Ograniczenia dla tabeli `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`chat`) REFERENCES `chats` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
