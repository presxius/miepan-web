-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 23, 2025 at 07:07 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `miepan_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id_admin` varchar(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_lengkap` varchar(100) DEFAULT NULL,
  `akses_level` enum('admin','kepala_admin') NOT NULL DEFAULT 'admin',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id_admin`, `username`, `password`, `nama_lengkap`, `akses_level`, `created_at`, `updated_at`) VALUES
('ADM-20250623001', 'ezra', '$2y$10$Z8e00Ez5SsIZwhq7ZCxTkubzaGCUrUTDqg4I6honr9Vka.AhIJPeS', 'Ezra Naj', 'kepala_admin', '2025-06-23 16:44:01', '2025-06-23 23:44:38'),
('ADM-20250623002', 'jaewo', '$2y$10$24RhVrVpwQhesSijONmnK.ykBUdPYWo1ykECbm3grfYzCep8Fbdiq', 'Jaewo', 'admin', '2025-06-23 16:45:25', '2025-06-23 16:45:25');

-- --------------------------------------------------------

--
-- Table structure for table `detail_pesanan`
--

CREATE TABLE `detail_pesanan` (
  `id_detail_pesanan` varchar(20) NOT NULL,
  `id_pesanan` varchar(20) NOT NULL,
  `id_menu` varchar(20) NOT NULL,
  `total_harga` decimal(10,2) NOT NULL,
  `jumlah_pesanan` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_pesanan`
--

INSERT INTO `detail_pesanan` (`id_detail_pesanan`, `id_pesanan`, `id_menu`, `total_harga`, `jumlah_pesanan`, `created_at`, `updated_at`) VALUES
('DTL-20250623001', 'PSN-20250623001', 'MNU-20250623001', 5000.00, 1, '2025-06-23 16:50:27', '2025-06-23 16:50:27'),
('DTL-20250623002', 'PSN-20250623001', 'MNU-20250623002', 30000.00, 2, '2025-06-23 16:50:27', '2025-06-23 16:50:27');

-- --------------------------------------------------------

--
-- Table structure for table `menu`
--

CREATE TABLE `menu` (
  `id_menu` varchar(20) NOT NULL,
  `nama_menu` varchar(100) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `harga` int(11) NOT NULL,
  `gambar` varchar(255) DEFAULT NULL,
  `kategori` enum('makanan','minuman') NOT NULL,
  `status` enum('tersedia','tidak tersedia') DEFAULT 'tersedia',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu`
--

INSERT INTO `menu` (`id_menu`, `nama_menu`, `deskripsi`, `harga`, `gambar`, `kategori`, `status`, `created_at`, `updated_at`) VALUES
('MNU-20250623001', 'Teh Hangat', 'Teh Manis Hangat', 5000, '1750697245_76dd9ea306be89f6982f.jpg', 'minuman', 'tersedia', '2025-06-23 16:47:25', '2025-06-23 16:47:25'),
('MNU-20250623002', 'Mie Pakistan', 'Mie Goreng', 15000, '1750697280_f7d8382b4eeaa9c5dc41.jpg', 'makanan', 'tersedia', '2025-06-23 16:48:00', '2025-06-23 16:48:00'),
('MNU-20250623003', 'Mie Bangladesh', 'Mie Rebus', 15000, '1750697311_3372c193df7540cd1c2f.jpg', 'makanan', 'tersedia', '2025-06-23 16:48:31', '2025-06-23 16:48:31'),
('MNU-20250623004', 'Es Timun', 'Es timun segar', 7000, '1750697345_21e0f20ad67571f2d985.jpg', 'minuman', 'tidak tersedia', '2025-06-23 16:49:05', '2025-06-23 16:49:05'),
('MNU-20250623005', 'Es Teh ', 'Es Teh Manis', 5000, '1750697376_f50de8451059f0831666.jpg', 'minuman', 'tersedia', '2025-06-23 16:49:36', '2025-06-23 16:49:36');

-- --------------------------------------------------------

--
-- Table structure for table `pesanan`
--

CREATE TABLE `pesanan` (
  `id_pesanan` varchar(20) NOT NULL,
  `nama_pemesan` varchar(100) DEFAULT NULL,
  `waktu_pesan` datetime DEFAULT current_timestamp(),
  `status_pesanan` enum('pending','diproses','sudah selesai') NOT NULL DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pesanan`
--

INSERT INTO `pesanan` (`id_pesanan`, `nama_pemesan`, `waktu_pesan`, `status_pesanan`, `created_at`, `updated_at`) VALUES
('PSN-20250623001', 'Radit', '2025-06-23 16:50:27', 'sudah selesai', '2025-06-23 16:50:27', '2025-06-23 16:56:41');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id_admin`);

--
-- Indexes for table `detail_pesanan`
--
ALTER TABLE `detail_pesanan`
  ADD PRIMARY KEY (`id_detail_pesanan`),
  ADD KEY `detail_pesanan_ibfk_2` (`id_menu`),
  ADD KEY `detail_pesanan_ibfk_1` (`id_pesanan`);

--
-- Indexes for table `menu`
--
ALTER TABLE `menu`
  ADD PRIMARY KEY (`id_menu`);

--
-- Indexes for table `pesanan`
--
ALTER TABLE `pesanan`
  ADD PRIMARY KEY (`id_pesanan`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `detail_pesanan`
--
ALTER TABLE `detail_pesanan`
  ADD CONSTRAINT `detail_pesanan_ibfk_1` FOREIGN KEY (`id_pesanan`) REFERENCES `pesanan` (`id_pesanan`) ON DELETE CASCADE,
  ADD CONSTRAINT `detail_pesanan_ibfk_2` FOREIGN KEY (`id_menu`) REFERENCES `menu` (`id_menu`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
