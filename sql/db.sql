-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2025-02-10 16:56:56.654

-- tables
-- Table: Ambiente
CREATE TABLE `Ambiente` (
    `id_ambiente` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `descripcion` nvarchar(30)  NOT NULL,
    CONSTRAINT `Ambiente_pk` PRIMARY KEY (`id_ambiente`)
);

-- Table: Ambiente_Vivienda
CREATE TABLE `Ambiente_Vivienda` (
    `id_am_vi` int  NOT NULL,
    `Ambiente_id` int  NOT NULL,
    `Vivienda_id` int  NOT NULL,
    CONSTRAINT `Ambiente_Vivienda_pk` PRIMARY KEY (`id_am_vi`)
);

-- Table: Clientes_Potenciales
CREATE TABLE `Clientes_Potenciales` (
    `id_clientes` int  NOT NULL,
    `fecha_contacto` datetime  NOT NULL,
    `mensaje` nvarchar(20)  NOT NULL,
    `Usuario_id_usuario` int  NOT NULL,
    `Publicacion_id_publicacion` int  NOT NULL,
    CONSTRAINT `Clientes_Potenciales_pk` PRIMARY KEY (`id_clientes`)
);

-- Table: Equipamiento
CREATE TABLE `Equipamiento` (
    `id_equipamiento` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `descripcion` nvarchar(10)  NOT NULL,
    CONSTRAINT `Equipamiento_pk` PRIMARY KEY (`id_equipamiento`)
);

-- Table: Equipamiento_Vehiculo
CREATE TABLE `Equipamiento_Vehiculo` (
    `id_equi_vehi` int  NOT NULL,
    `Vehiculo_id` int  NOT NULL,
    `Equipamiento_id` int  NOT NULL,
    CONSTRAINT `Equipamiento_Vehiculo_pk` PRIMARY KEY (`id_equi_vehi`)
);

-- Table: Notificacion
CREATE TABLE `Notificacion` (
    `id_notificacion` int  NOT NULL,
    `tipo_publicacion` nvarchar(10)  NOT NULL,
    `precio_rango_min` float(10,2)  NOT NULL,
    `precio_rango_max` float(10,2)  NOT NULL,
    `distrito_preferido` nvarchar(20)  NOT NULL,
    `Usuario_id_usuario` int  NOT NULL,
    `Publicacion_id_publicacion` int  NOT NULL,
    CONSTRAINT `Notificacion_pk` PRIMARY KEY (`id_notificacion`)
);

-- Table: Publicacion
CREATE TABLE `Publicacion` (
    `id_publicacion` int  NOT NULL,
    `fecha_publicacion` datetime  NOT NULL,
    `titulo` nvarchar(10)  NOT NULL,
    `descripcion` nvarchar(50)  NOT NULL,
    `precio_unitario` float(10,2)  NOT NULL,
    `distrito` nvarchar(10)  NOT NULL,
    `direccion` nvarchar(30)  NOT NULL,
    `latitud` int  NOT NULL,
    `longitud` int  NOT NULL,
    `estado` nvarchar(10)  NOT NULL,
    `imagenes` json  NOT NULL,
    `Usuario_id_usuario` int  NOT NULL,
    `Vivienda_id_vivienda` int  NOT NULL,
    `Vehiculo_id_vehiculo` int  NOT NULL,
    CONSTRAINT `Publicacion_pk` PRIMARY KEY (`id_publicacion`)
);

-- Table: Seguro
CREATE TABLE `Seguro` (
    `id_seguro` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `descripcion` nvarchar(10)  NOT NULL,
    CONSTRAINT `Seguro_pk` PRIMARY KEY (`id_seguro`)
);

-- Table: Servicio
CREATE TABLE `Servicio` (
    `id_servicio` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `descripcion` nvarchar(30)  NOT NULL,
    CONSTRAINT `Servicio_pk` PRIMARY KEY (`id_servicio`)
);

-- Table: Servicio_Vivienda
CREATE TABLE `Servicio_Vivienda` (
    `id_ser_vi` int  NOT NULL,
    `Servicio_id` int  NOT NULL,
    `Vivienda_id` int  NOT NULL,
    CONSTRAINT `Servicio_Vivienda_pk` PRIMARY KEY (`id_ser_vi`)
);

-- Table: Tipo_usuario
CREATE TABLE `Tipo_usuario` (
    `id_tipo_u` int  NOT NULL,
    `nombre` nvarchar(15)  NOT NULL,
    CONSTRAINT `Tipo_usuario_pk` PRIMARY KEY (`id_tipo_u`)
);

-- Table: Tipo_vehiculo
CREATE TABLE `Tipo_vehiculo` (
    `id_tipo_ve` int  NOT NULL,
    `nombre` nvarchar(20)  NOT NULL,
    `Vehiculo_id_vehiculo` int  NOT NULL,
    CONSTRAINT `Tipo_vehiculo_pk` PRIMARY KEY (`id_tipo_ve`)
);

-- Table: Tipo_vivienda
CREATE TABLE `Tipo_vivienda` (
    `id_tipo_v` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `capacidad` int  NOT NULL,
    `pisos` int  NOT NULL,
    CONSTRAINT `Tipo_vivienda_pk` PRIMARY KEY (`id_tipo_v`)
);

-- Table: Usuario
CREATE TABLE `Usuario` (
    `id_usuario` int  NOT NULL,
    `nombre` nvarchar(10)  NOT NULL,
    `correo` nvarchar(10)  NOT NULL,
    `contrasenia` nvarchar(15)  NOT NULL,
    `doc_identidad` nvarchar(10)  NOT NULL,
    `telefono` nvarchar(11)  NOT NULL,
    `direccion` nvarchar(30)  NOT NULL,
    `fecha_ingreso` datetime  NOT NULL,
    `preferencias` nvarchar(10)  NOT NULL,
    `imagen_url` nvarchar(20)  NOT NULL,
    `Tipo_usuario_id_tipo_u` int  NOT NULL,
    CONSTRAINT `Usuario_pk` PRIMARY KEY (`id_usuario`)
);

-- Table: Vehiculo
CREATE TABLE `Vehiculo` (
    `id_vehiculo` int  NOT NULL,
    `marca` nvarchar(10)  NOT NULL,
    `modelo` nvarchar(20)  NOT NULL,
    `anio` date  NOT NULL,
    `placa` nvarchar(10)  NOT NULL,
    `color` nvarchar(10)  NOT NULL,
    `transmision` nvarchar(10)  NOT NULL,
    `cant_combustible` nvarchar(10)  NOT NULL,
    `tipo_combustible` nvarchar(10)  NOT NULL,
    `kilometraje` nvarchar(10)  NOT NULL,
    `Tipo_vechiculo_id` int  NOT NULL,
    `Seguro_id_seguro` int  NOT NULL,
    CONSTRAINT `Vehiculo_pk` PRIMARY KEY (`id_vehiculo`)
);

-- Table: Vivienda
CREATE TABLE `Vivienda` (
    `id_vivienda` int  NOT NULL,
    `fecha_construccion` datetime  NOT NULL,
    `dimensiones` nvarchar(15)  NOT NULL,
    `antiguedad` date  NOT NULL,
    `Tipo_vivienda_id` int  NOT NULL,
    CONSTRAINT `Vivienda_pk` PRIMARY KEY (`id_vivienda`)
);

-- foreign keys
-- Reference: Ambiente_Vivienda_Ambiente (table: Ambiente_Vivienda)
ALTER TABLE `Ambiente_Vivienda` ADD CONSTRAINT `Ambiente_Vivienda_Ambiente` FOREIGN KEY `Ambiente_Vivienda_Ambiente` (`Ambiente_id`)
    REFERENCES `Ambiente` (`id_ambiente`);

-- Reference: Ambiente_Vivienda_Vivienda (table: Ambiente_Vivienda)
ALTER TABLE `Ambiente_Vivienda` ADD CONSTRAINT `Ambiente_Vivienda_Vivienda` FOREIGN KEY `Ambiente_Vivienda_Vivienda` (`Vivienda_id`)
    REFERENCES `Vivienda` (`id_vivienda`);

-- Reference: Clientes_Potenciales_Publicacion (table: Clientes_Potenciales)
ALTER TABLE `Clientes_Potenciales` ADD CONSTRAINT `Clientes_Potenciales_Publicacion` FOREIGN KEY `Clientes_Potenciales_Publicacion` (`Publicacion_id_publicacion`)
    REFERENCES `Publicacion` (`id_publicacion`);

-- Reference: Clientes_Potenciales_Usuario (table: Clientes_Potenciales)
ALTER TABLE `Clientes_Potenciales` ADD CONSTRAINT `Clientes_Potenciales_Usuario` FOREIGN KEY `Clientes_Potenciales_Usuario` (`Usuario_id_usuario`)
    REFERENCES `Usuario` (`id_usuario`);

-- Reference: Equipamiento_Vehiculo_Equipamiento (table: Equipamiento_Vehiculo)
ALTER TABLE `Equipamiento_Vehiculo` ADD CONSTRAINT `Equipamiento_Vehiculo_Equipamiento` FOREIGN KEY `Equipamiento_Vehiculo_Equipamiento` (`Equipamiento_id`)
    REFERENCES `Equipamiento` (`id_equipamiento`);

-- Reference: Equipamiento_Vehiculo_Vehiculo (table: Equipamiento_Vehiculo)
ALTER TABLE `Equipamiento_Vehiculo` ADD CONSTRAINT `Equipamiento_Vehiculo_Vehiculo` FOREIGN KEY `Equipamiento_Vehiculo_Vehiculo` (`Vehiculo_id`)
    REFERENCES `Vehiculo` (`id_vehiculo`);

-- Reference: Notificacion_Publicacion (table: Notificacion)
ALTER TABLE `Notificacion` ADD CONSTRAINT `Notificacion_Publicacion` FOREIGN KEY `Notificacion_Publicacion` (`Publicacion_id_publicacion`)
    REFERENCES `Publicacion` (`id_publicacion`);

-- Reference: Notificacion_Usuario (table: Notificacion)
ALTER TABLE `Notificacion` ADD CONSTRAINT `Notificacion_Usuario` FOREIGN KEY `Notificacion_Usuario` (`Usuario_id_usuario`)
    REFERENCES `Usuario` (`id_usuario`);

-- Reference: Publicacion_Usuario (table: Publicacion)
ALTER TABLE `Publicacion` ADD CONSTRAINT `Publicacion_Usuario` FOREIGN KEY `Publicacion_Usuario` (`Usuario_id_usuario`)
    REFERENCES `Usuario` (`id_usuario`);

-- Reference: Publicacion_Vehiculo (table: Publicacion)
ALTER TABLE `Publicacion` ADD CONSTRAINT `Publicacion_Vehiculo` FOREIGN KEY `Publicacion_Vehiculo` (`Vehiculo_id_vehiculo`)
    REFERENCES `Vehiculo` (`id_vehiculo`);

-- Reference: Publicacion_Vivienda (table: Publicacion)
ALTER TABLE `Publicacion` ADD CONSTRAINT `Publicacion_Vivienda` FOREIGN KEY `Publicacion_Vivienda` (`Vivienda_id_vivienda`)
    REFERENCES `Vivienda` (`id_vivienda`);

-- Reference: Servicio_Vivienda_Servicio (table: Servicio_Vivienda)
ALTER TABLE `Servicio_Vivienda` ADD CONSTRAINT `Servicio_Vivienda_Servicio` FOREIGN KEY `Servicio_Vivienda_Servicio` (`Servicio_id`)
    REFERENCES `Servicio` (`id_servicio`);

-- Reference: Servicio_Vivienda_Vivienda (table: Servicio_Vivienda)
ALTER TABLE `Servicio_Vivienda` ADD CONSTRAINT `Servicio_Vivienda_Vivienda` FOREIGN KEY `Servicio_Vivienda_Vivienda` (`Vivienda_id`)
    REFERENCES `Vivienda` (`id_vivienda`);

-- Reference: Tipo_vehiculo_Vehiculo (table: Vehiculo)
ALTER TABLE `Vehiculo` ADD CONSTRAINT `Tipo_vehiculo_Vehiculo` FOREIGN KEY `Tipo_vehiculo_Vehiculo` (`Tipo_vechiculo_id`)
    REFERENCES `Tipo_vehiculo` (`id_tipo_ve`);

-- Reference: Tipo_vivienda_Vivienda (table: Vivienda)
ALTER TABLE `Vivienda` ADD CONSTRAINT `Tipo_vivienda_Vivienda` FOREIGN KEY `Tipo_vivienda_Vivienda` (`Tipo_vivienda_id`)
    REFERENCES `Tipo_vivienda` (`id_tipo_v`);

-- Reference: Usuario_Tipo_usuario (table: Usuario)
ALTER TABLE `Usuario` ADD CONSTRAINT `Usuario_Tipo_usuario` FOREIGN KEY `Usuario_Tipo_usuario` (`Tipo_usuario_id_tipo_u`)
    REFERENCES `Tipo_usuario` (`id_tipo_u`);

-- Reference: Vehiculo_Seguro (table: Vehiculo)
ALTER TABLE `Vehiculo` ADD CONSTRAINT `Vehiculo_Seguro` FOREIGN KEY `Vehiculo_Seguro` (`Seguro_id_seguro`)
    REFERENCES `Seguro` (`id_seguro`);

-- End of file.

