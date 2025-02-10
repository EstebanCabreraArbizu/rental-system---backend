create table products(
	id_products INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL UNIQUE,
    unit_price FLOAT4 NOT NULL,
    stock INT2 NOT NULL,
    PRIMARY KEY(id_products)
);