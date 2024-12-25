CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    height INT NOT NULL,
    weight INT NOT NULL,
    age INT NOT NULL,
    gender INT NOT NULL,
    highBloodPressure VARCHAR(10) NOT NULL,
    highBloodSugar TINYINT(1) NOT NULL,
    highCholesterol TINYINT(1) NOT NULL,
    heavyAlcohol TINYINT(1) NOT NULL,
    smoking TINYINT(1) NOT NULL,
    stroke TINYINT(1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_id INT,
    PRIMARY KEY (id)
);