
CREATE TABLE `dat_master` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `record_id` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  `container_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `assignment_id` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `route_no` varchar(6) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stop_scan` tinyint(1) NOT NULL DEFAULT '0',
  `pick_area` varchar(6) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pick_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jurisdiction` varchar(6) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `carton_qty` varchar(4) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stop_no` varchar(4) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `c_comp` tinyint(4) DEFAULT '0',
  `a_comp` tinyint(4) DEFAULT '0',
  `o_comp` tinyint(4) DEFAULT '0',
  `r_comp` tinyint(4) DEFAULT '0',
  `assign_name` varchar(125) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=481 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;