CREATE DATABASE RENTALLDB
GO

USE RENTALLDB
GO

CREATE TABLE Ambiente (
    id_ambiente INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    descripcion NVARCHAR(30) NOT NULL,
    CONSTRAINT Ambiente_pk PRIMARY KEY (id_ambiente)
);

-- Table: Ambiente_Vivienda
CREATE TABLE Ambiente_Vivienda (
    id_am_vi INT NOT NULL,
    Ambiente_id INT NOT NULL,
    Vivienda_id INT NOT NULL,
    CONSTRAINT Ambiente_Vivienda_pk PRIMARY KEY (id_am_vi)
);

-- Table: Clientes_Potenciales
CREATE TABLE Clientes_Potenciales (
    id_clientes INT NOT NULL,
    fecha_contacto DATETIME NOT NULL,
    mensaje NVARCHAR(20) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Publicacion_id_publicacion INT NOT NULL,
    CONSTRAINT Clientes_Potenciales_pk PRIMARY KEY (id_clientes)
);

-- Table: Equipamiento
CREATE TABLE Equipamiento (
    id_equipamiento INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    descripcion NVARCHAR(10) NOT NULL,
    CONSTRAINT Equipamiento_pk PRIMARY KEY (id_equipamiento)
);

-- Table: Equipamiento_Vehiculo
CREATE TABLE Equipamiento_Vehiculo (
    id_equi_vehi INT NOT NULL,
    Vehiculo_id INT NOT NULL,
    Equipamiento_id INT NOT NULL,
    CONSTRAINT Equipamiento_Vehiculo_pk PRIMARY KEY (id_equi_vehi)
);

-- Table: Notificacion
CREATE TABLE Notificacion (
    id_notificacion INT NOT NULL,
    tipo_publicacion NVARCHAR(10) NOT NULL,
    precio_rango_min DECIMAL(10,2) NOT NULL,
    precio_rango_max DECIMAL(10,2) NOT NULL,
    distrito_preferido NVARCHAR(255) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Publicacion_id_publicacion INT NOT NULL,
    CONSTRAINT Notificacion_pk PRIMARY KEY (id_notificacion)
);


-- Table: Publicacion
CREATE TABLE Publicacion (
    id_publicacion INT NOT NULL,
    fecha_publicacion DATETIME NOT NULL,
    titulo NVARCHAR(10) NOT NULL,
    descripcion NVARCHAR(50) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    distrito NVARCHAR(10) NOT NULL,
    direccion NVARCHAR(30) NOT NULL,
    latitud INT NOT NULL,
    longitud INT NOT NULL,
    estado NVARCHAR(10) NOT NULL,
    imagenes NVARCHAR(MAX) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Vivienda_id_vivienda INT NOT NULL,
    Vehiculo_id_vehiculo INT NOT NULL,
    CONSTRAINT Publicacion_pk PRIMARY KEY (id_publicacion)
);

-- Table: Seguro
CREATE TABLE Seguro (
    id_seguro INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    descripcion NVARCHAR(10) NOT NULL,
    CONSTRAINT Seguro_pk PRIMARY KEY (id_seguro)
);

-- Table: Servicio
CREATE TABLE Servicio (
    id_servicio INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    descripcion NVARCHAR(30) NOT NULL,
    CONSTRAINT Servicio_pk PRIMARY KEY (id_servicio)
);

-- Table: Servicio_Vivienda
CREATE TABLE Servicio_Vivienda (
    id_ser_vi INT NOT NULL,
    Servicio_id INT NOT NULL,
    Vivienda_id INT NOT NULL,
    CONSTRAINT Servicio_Vivienda_pk PRIMARY KEY (id_ser_vi)
);

-- Table: Tipo_usuario
CREATE TABLE Tipo_usuario (
    id_tipo_u INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    CONSTRAINT Tipo_usuario_pk PRIMARY KEY (id_tipo_u)
);

-- Table: Tipo_vehiculo
CREATE TABLE Tipo_vehiculo (
    id_tipo_ve INT NOT NULL,
    nombre NVARCHAR(20) NOT NULL,
    Vehiculo_id_vehiculo INT NOT NULL,
    CONSTRAINT Tipo_vehiculo_pk PRIMARY KEY (id_tipo_ve)
);

-- Table: Tipo_vivienda
CREATE TABLE Tipo_vivienda (
    id_tipo_v INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    capacidad INT NOT NULL,
    pisos INT NOT NULL,
    CONSTRAINT Tipo_vivienda_pk PRIMARY KEY (id_tipo_v)
);

-- Table: Usuario
CREATE TABLE Usuario (
    id_usuario INT NOT NULL,
    nombre NVARCHAR(10) NOT NULL,
    correo NVARCHAR(10) NOT NULL,
    contrasenia NVARCHAR(15) NOT NULL,
    doc_identidad NVARCHAR(10) NOT NULL,
    telefono NVARCHAR(11) NOT NULL,
    direccion NVARCHAR(30) NOT NULL,
    fecha_ingreso DATETIME NOT NULL,
    preferencias NVARCHAR(10) NOT NULL,
    imagen_url NVARCHAR(20) NOT NULL,
    Tipo_usuario_id_tipo_u INT NOT NULL,
    CONSTRAINT Usuario_pk PRIMARY KEY (id_usuario)
);

-- Table: Vehiculo
CREATE TABLE Vehiculo (
    id_vehiculo INT NOT NULL,
    marca NVARCHAR(10) NOT NULL,
    modelo NVARCHAR(20) NOT NULL,
    anio DATE NOT NULL,
    placa NVARCHAR(10) NOT NULL,
    color NVARCHAR(10) NOT NULL,
    transmision NVARCHAR(10) NOT NULL,
    cant_combustible NVARCHAR(10) NOT NULL,
    tipo_combustible NVARCHAR(10) NOT NULL,
    kilometraje NVARCHAR(10) NOT NULL,
    Tipo_vechiculo_id INT NOT NULL,
    Seguro_id_seguro INT NOT NULL,
    CONSTRAINT Vehiculo_pk PRIMARY KEY (id_vehiculo)
);

-- Table: Vivienda
CREATE TABLE Vivienda (
    id_vivienda INT NOT NULL,
    fecha_construccion DATETIME NOT NULL,
    dimensiones NVARCHAR(15) NOT NULL,
    antiguedad DATE NOT NULL,
    Tipo_vivienda_id INT NOT NULL,
    CONSTRAINT Vivienda_pk PRIMARY KEY (id_vivienda)
);

-- Foreign keys

-- Reference: Ambiente_Vivienda_Ambiente (table: Ambiente_Vivienda)
ALTER TABLE Ambiente_Vivienda
ADD CONSTRAINT Ambiente_Vivienda_Ambiente FOREIGN KEY (Ambiente_id) REFERENCES Ambiente (id_ambiente);

-- Reference: Ambiente_Vivienda_Vivienda (table: Ambiente_Vivienda)
ALTER TABLE Ambiente_Vivienda
ADD CONSTRAINT Ambiente_Vivienda_Vivienda FOREIGN KEY (Vivienda_id) REFERENCES Vivienda (id_vivienda);

-- Reference: Clientes_Potenciales_Publicacion (table: Clientes_Potenciales)
ALTER TABLE Clientes_Potenciales
ADD CONSTRAINT Clientes_Potenciales_Publicacion FOREIGN KEY (Publicacion_id_publicacion) REFERENCES Publicacion (id_publicacion);

-- Reference: Clientes_Potenciales_Usuario (table: Clientes_Potenciales)
ALTER TABLE Clientes_Potenciales
ADD CONSTRAINT Clientes_Potenciales_Usuario FOREIGN KEY (Usuario_id_usuario) REFERENCES Usuario (id_usuario);

-- Reference: Equipamiento_Vehiculo_Equipamiento (table: Equipamiento_Vehiculo)
ALTER TABLE Equipamiento_Vehiculo
ADD CONSTRAINT Equipamiento_Vehiculo_Equipamiento FOREIGN KEY (Equipamiento_id) REFERENCES Equipamiento (id_equipamiento);

-- Reference: Equipamiento_Vehiculo_Vehiculo (table: Equipamiento_Vehiculo)
ALTER TABLE Equipamiento_Vehiculo
ADD CONSTRAINT Equipamiento_Vehiculo_Vehiculo FOREIGN KEY (Vehiculo_id) REFERENCES Vehiculo (id_vehiculo);

-- Reference: Notificacion_Publicacion (table: Notificacion)
ALTER TABLE Notificacion
ADD CONSTRAINT Notificacion_Publicacion FOREIGN KEY (Publicacion_id_publicacion) REFERENCES Publicacion (id_publicacion);

-- Reference: Notificacion_Usuario (table: Notificacion)
ALTER TABLE Notificacion
ADD CONSTRAINT Notificacion_Usuario FOREIGN KEY (Usuario_id_usuario) REFERENCES Usuario (id_usuario);

-- Reference: Publicacion_Usuario (table: Publicacion)
ALTER TABLE Publicacion
ADD CONSTRAINT Publicacion_Usuario FOREIGN KEY (Usuario_id_usuario) REFERENCES Usuario (id_usuario);

-- Reference: Publicacion_Vehiculo (table: Publicacion)
ALTER TABLE Publicacion
ADD CONSTRAINT Publicacion_Vehiculo FOREIGN KEY (Vehiculo_id_vehiculo) REFERENCES Vehiculo (id_vehiculo);

-- Reference: Publicacion_Vivienda (table: Publicacion)
ALTER TABLE Publicacion
ADD CONSTRAINT Publicacion_Vivienda FOREIGN KEY (Vivienda_id_vivienda) REFERENCES Vivienda (id_vivienda);

-- Reference: Servicio_Vivienda_Servicio (table: Servicio_Vivienda)
ALTER TABLE Servicio_Vivienda
ADD CONSTRAINT Servicio_Vivienda_Servicio FOREIGN KEY (Servicio_id) REFERENCES Servicio (id_servicio);

-- Reference: Servicio_Vivienda_Vivienda (table: Servicio_Vivienda)
ALTER TABLE Servicio_Vivienda
ADD CONSTRAINT Servicio_Vivienda_Vivienda FOREIGN KEY (Vivienda_id) REFERENCES Vivienda (id_vivienda);

-- Reference: Tipo_vehiculo_Vehiculo (table: Vehiculo)
ALTER TABLE Vehiculo
ADD CONSTRAINT Tipo_vehiculo_Vehiculo FOREIGN KEY (Tipo_vechiculo_id) REFERENCES Tipo_vehiculo (id_tipo_ve);

-- Reference: Tipo_vivienda_Vivienda (table: Vivienda)
ALTER TABLE Vivienda
ADD CONSTRAINT Tipo_vivienda_Vivienda FOREIGN KEY (Tipo_vivienda_id) REFERENCES Tipo_vivienda (id_tipo_v);

-- Reference: Usuario_Tipo_usuario (table: Usuario)
ALTER TABLE Usuario
ADD CONSTRAINT Usuario_Tipo_usuario FOREIGN KEY (Tipo_usuario_id_tipo_u) REFERENCES Tipo_usuario (id_tipo_u);

-- Reference: Vehiculo_Seguro (table: Vehiculo)
ALTER TABLE Vehiculo
ADD CONSTRAINT Vehiculo_Seguro FOREIGN KEY (Seguro_id_seguro) REFERENCES Seguro (id_seguro);

-- End of file