CREATE DATABASE login;

CREATE TABLE `actividad_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `fecha_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo_movimiento` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=270 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `comentarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_publicacion` int NOT NULL,
  `id_usuario` int NOT NULL,
  `contenido` text COLLATE utf8mb4_general_ci,
  `fecha_comentario` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `imagen` longblob,
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`),
  KEY `comentarios_ibfk_1` (`id_publicacion`),
  CONSTRAINT `comentarios_ibfk_1` FOREIGN KEY (`id_publicacion`) REFERENCES `publicaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `comentarios_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `informacion_personal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `estado` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `musica` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `edad` int DEFAULT NULL,
  `pasatiempos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `direccion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `trabajo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `informacion_personal_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `publicaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `contenido` text,
  `fecha_publicacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `imagen` longblob,
  `num_likes` int DEFAULT '0',
  `num_loves` int DEFAULT '0',
  `num_wows` int DEFAULT '0',
  `num_sads` int DEFAULT '0',
  `num_angrys` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `publicaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `reacciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_publicacion` int NOT NULL,
  `id_usuario` int NOT NULL,
  `tipo_reaccion` enum('like','love','haha','wow','sad','angry') COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`),
  KEY `reacciones_ibfk_1` (`id_publicacion`),
  CONSTRAINT `reacciones_ibfk_1` FOREIGN KEY (`id_publicacion`) REFERENCES `publicaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reacciones_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `correo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `id_rol` int NOT NULL,
  `avatar` longblob,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


mysql -u root -p