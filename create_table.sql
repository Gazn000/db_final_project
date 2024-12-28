CREATE TABLE account (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

-- Create table for the other data
CREATE TABLE health_data (
    id INT NOT NULL AUTO_INCREMENT,
    height INT NOT NULL,
    weight INT NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    highBloodPressure TINYINT(1) NOT NULL,
    highBloodSugar TINYINT(1) NOT NULL,
    highCholesterol TINYINT(1) NOT NULL,
    heavyAlcohol TINYINT(1) NOT NULL,
    smoking TINYINT(1) NOT NULL,
    stroke TINYINT(1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_id INT NOT NULL,
    record_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
);