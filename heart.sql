-- 創建 HeartDiseaseHealthIndicators 表
CREATE TABLE Heart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    HeartDiseaseorAttack TINYINT NOT NULL,
    HighBP TINYINT NOT NULL,
    HighChol TINYINT NOT NULL,
    CholCheck TINYINT NOT NULL,
    BMI DECIMAL(5,2) NOT NULL,
    Smoker TINYINT NOT NULL,
    Stroke TINYINT NOT NULL,
    Diabetes INT NOT NULL,
    HvyAlcoholConsump TINYINT NOT NULL,
    Sex TINYINT NOT NULL,
    Age INT NOT NULL
);
ALTER TABLE Heart AUTO_INCREMENT = 1;

-- 從 CSV 文件加載數據
LOAD DATA INFILE '/mnt/c/var/lib/mysql-files/heart_disease_health_indicators_BRFSS2015.csv' 
INTO TABLE Heart
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(HeartDiseaseorAttack, HighBP, HighChol, CholCheck, BMI, Smoker, Stroke, Diabetes, 
@hysActivity, @Fruits, @Veggies, HvyAlcoholConsump, @AnyHealthcare, @NoDocbcCost, 
@GenHlth, @MentHlth, @PhysHlth, @DiffWalk, Sex, Age, @Education, @Income);
