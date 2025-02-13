CREATE DATABASE RENTALLDB2
GO

USE RENTALLDB2
GO

-- Tablas base (sin dependencias)
CREATE TABLE Tipo_usuario (
    id_tipo_u INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(20) NOT NULL,
    CONSTRAINT Tipo_usuario_pk PRIMARY KEY (id_tipo_u)
);

CREATE TABLE Tipo_vivienda (
    id_tipo_v INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    pisos INT NOT NULL,
    CONSTRAINT Tipo_vivienda_pk PRIMARY KEY (id_tipo_v)
);

CREATE TABLE Tipo_vehiculo (
    id_tipo_ve INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    CONSTRAINT Tipo_vehiculo_pk PRIMARY KEY (id_tipo_ve)
);

CREATE TABLE Seguro (
    id_seguro INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(500) NOT NULL,
    CONSTRAINT Seguro_pk PRIMARY KEY (id_seguro)
);

CREATE TABLE Ambiente (
    id_ambiente INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(200) NOT NULL,
    CONSTRAINT Ambiente_pk PRIMARY KEY (id_ambiente)
);

CREATE TABLE Servicio (
    id_servicio INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(200) NOT NULL,
    CONSTRAINT Servicio_pk PRIMARY KEY (id_servicio)
);

CREATE TABLE Equipamiento (
    id_equipamiento INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(200) NOT NULL,
    CONSTRAINT Equipamiento_pk PRIMARY KEY (id_equipamiento)
);

-- Tablas con dependencias primarias
CREATE TABLE Usuario (
    id_usuario INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    correo NVARCHAR(100) NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    doc_identidad NVARCHAR(20) NOT NULL,
    telefono NVARCHAR(20) NOT NULL,
    direccion NVARCHAR(200) NOT NULL,
    fecha_ingreso DATETIME DEFAULT GETDATE() NOT NULL,
    preferencias NVARCHAR(MAX) NULL,
    imagen_url NVARCHAR(500) NOT NULL,
    Tipo_usuario_id_tipo_u INT NOT NULL,
    CONSTRAINT Usuario_pk PRIMARY KEY (id_usuario),
    CONSTRAINT Usuario_Tipo_usuario FOREIGN KEY (Tipo_usuario_id_tipo_u) 
        REFERENCES Tipo_usuario (id_tipo_u)
);

CREATE TABLE Vivienda (
    id_vivienda INT IDENTITY(1,1) NOT NULL,
    fecha_construccion DATETIME NOT NULL,
    dimensiones NVARCHAR(50) NOT NULL,
    antiguedad DATE NOT NULL,
    Tipo_vivienda_id INT NOT NULL,
    CONSTRAINT Vivienda_pk PRIMARY KEY (id_vivienda),
    CONSTRAINT Tipo_vivienda_Vivienda FOREIGN KEY (Tipo_vivienda_id) 
        REFERENCES Tipo_vivienda (id_tipo_v)
);

CREATE TABLE Vehiculo (
    id_vehiculo INT IDENTITY(1,1) NOT NULL,
    marca NVARCHAR(50) NOT NULL,
    modelo NVARCHAR(50) NOT NULL,
    anio DATE NOT NULL,
    placa NVARCHAR(20) NOT NULL,
    color NVARCHAR(30) NOT NULL,
    transmision NVARCHAR(20) NOT NULL,
    cant_combustible NVARCHAR(20) NOT NULL,
    tipo_combustible NVARCHAR(20) NOT NULL,
    kilometraje NVARCHAR(20) NOT NULL,
    Tipo_vechiculo_id INT NOT NULL,
    Seguro_id_seguro INT NOT NULL,
    CONSTRAINT Vehiculo_pk PRIMARY KEY (id_vehiculo),
    CONSTRAINT Tipo_vehiculo_Vehiculo FOREIGN KEY (Tipo_vechiculo_id) 
        REFERENCES Tipo_vehiculo (id_tipo_ve),
    CONSTRAINT Vehiculo_Seguro FOREIGN KEY (Seguro_id_seguro) 
        REFERENCES Seguro (id_seguro)
);

-- Tablas con dependencias secundarias
CREATE TABLE Publicacion (
    id_publicacion INT IDENTITY(1,1) NOT NULL,
    fecha_publicacion DATETIME DEFAULT GETDATE() NOT NULL,
    titulo NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(500) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    distrito NVARCHAR(50) NOT NULL,
    direccion NVARCHAR(200) NOT NULL,
    latitud DECIMAL(9,6) NOT NULL,
    longitud DECIMAL(9,6) NOT NULL,
    estado NVARCHAR(20) NOT NULL,
    imagenes NVARCHAR(MAX) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Vivienda_id_vivienda INT NULL,
    Vehiculo_id_vehiculo INT NULL,
    CONSTRAINT Publicacion_pk PRIMARY KEY (id_publicacion),
    CONSTRAINT Publicacion_Usuario FOREIGN KEY (Usuario_id_usuario) 
        REFERENCES Usuario (id_usuario),
    CONSTRAINT Publicacion_Vivienda FOREIGN KEY (Vivienda_id_vivienda) 
        REFERENCES Vivienda (id_vivienda),
    CONSTRAINT Publicacion_Vehiculo FOREIGN KEY (Vehiculo_id_vehiculo) 
        REFERENCES Vehiculo (id_vehiculo)
);

CREATE TABLE Ambiente_Vivienda (
    id_am_vi INT IDENTITY(1,1) NOT NULL,
    Ambiente_id INT NOT NULL,
    Vivienda_id INT NOT NULL,
    CONSTRAINT Ambiente_Vivienda_pk PRIMARY KEY (id_am_vi),
    CONSTRAINT Ambiente_Vivienda_Ambiente FOREIGN KEY (Ambiente_id) 
        REFERENCES Ambiente (id_ambiente),
    CONSTRAINT Ambiente_Vivienda_Vivienda FOREIGN KEY (Vivienda_id) 
        REFERENCES Vivienda (id_vivienda)
);

CREATE TABLE Servicio_Vivienda (
    id_ser_vi INT IDENTITY(1,1) NOT NULL,
    Servicio_id INT NOT NULL,
    Vivienda_id INT NOT NULL,
    CONSTRAINT Servicio_Vivienda_pk PRIMARY KEY (id_ser_vi),
    CONSTRAINT Servicio_Vivienda_Servicio FOREIGN KEY (Servicio_id) 
        REFERENCES Servicio (id_servicio),
    CONSTRAINT Servicio_Vivienda_Vivienda FOREIGN KEY (Vivienda_id) 
        REFERENCES Vivienda (id_vivienda)
);

CREATE TABLE Equipamiento_Vehiculo (
    id_equi_vehi INT IDENTITY(1,1) NOT NULL,
    Vehiculo_id INT NOT NULL,
    Equipamiento_id INT NOT NULL,
    CONSTRAINT Equipamiento_Vehiculo_pk PRIMARY KEY (id_equi_vehi),
    CONSTRAINT Equipamiento_Vehiculo_Vehiculo FOREIGN KEY (Vehiculo_id) 
        REFERENCES Vehiculo (id_vehiculo),
    CONSTRAINT Equipamiento_Vehiculo_Equipamiento FOREIGN KEY (Equipamiento_id) 
        REFERENCES Equipamiento (id_equipamiento)
);

CREATE TABLE Clientes_Potenciales (
    id_clientes INT IDENTITY(1,1) NOT NULL,
    fecha_contacto DATETIME DEFAULT GETDATE() NOT NULL,
    mensaje NVARCHAR(500) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Publicacion_id_publicacion INT NOT NULL,
    CONSTRAINT Clientes_Potenciales_pk PRIMARY KEY (id_clientes),
    CONSTRAINT Clientes_Potenciales_Usuario FOREIGN KEY (Usuario_id_usuario) 
        REFERENCES Usuario (id_usuario),
    CONSTRAINT Clientes_Potenciales_Publicacion FOREIGN KEY (Publicacion_id_publicacion) 
        REFERENCES Publicacion (id_publicacion)
);

CREATE TABLE Notificacion (
    id_notificacion INT IDENTITY(1,1) NOT NULL,
    tipo_publicacion NVARCHAR(50) NOT NULL,
    precio_rango_min DECIMAL(10,2) NOT NULL,
    precio_rango_max DECIMAL(10,2) NOT NULL,
    distrito_preferido NVARCHAR(255) NOT NULL,
    Usuario_id_usuario INT NOT NULL,
    Publicacion_id_publicacion INT NOT NULL,
    CONSTRAINT Notificacion_pk PRIMARY KEY (id_notificacion),
    CONSTRAINT Notificacion_Usuario FOREIGN KEY (Usuario_id_usuario) 
        REFERENCES Usuario (id_usuario),
    CONSTRAINT Notificacion_Publicacion FOREIGN KEY (Publicacion_id_publicacion) 
        REFERENCES Publicacion (id_publicacion)
);

-- Insertar tipos de usuario básicos
INSERT INTO Tipo_usuario (nombre) VALUES ('Cliente'), ('Propietario'), ('Administrador');


select * from Usuario