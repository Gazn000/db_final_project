CREATE TABLE diabetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    HighBP TINYINT,                    -- 血壓水平（（0:正常 1:高血壓 ）
    HighChol TINYINT,                  -- 膽固醇水平（0:正常 1:高膽固醇 ）
    BMI DECIMAL(5,2),                  -- 身體質量指數（BMI）
    Smoker TINYINT,                    -- 吸煙狀態（0: 非吸煙者, 1: 吸煙者）
    Stroke TINYINT,                    -- 中風(0:無 1:有)
    HeartDiseaseorAttack TINYINT,      -- 心血管疾病狀態（0: 無, 1: 有）
    PhysActivity TINYINT,              -- 身體活動狀態（0: 不活躍, 1: 活躍）
    HvyAlcoholConsump TINYINT,         -- 酒精消費（0: 不消費, 1: 消費）
    Sex TINYINT,                        -- 性別(0:female 1:male)
    Age TINYINT                   
);

LOAD DATA INFILE '/usr/local/mysql-files/FinalProject/diabetes_binary_5050split_health_indicators_BRFSS2015.csv' -- 用的時候記得改路徑
INTO TABLE diabetes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy, HighBP, HighChol, @dummy, BMI, Smoker, Stroke, HeartDiseaseorAttack, PhysActivity, @dummy, @dummy,HvyAlcoholConsump, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, Sex, Age, @dummy, @dummy);  -- 根據 CSV 中的欄位順序對應到 MySQL 表格的列

CREATE TABLE cardiovascular (
    id INT PRIMARY KEY,
    gender TINYINT, 
    height INT,
    weight INT, 
    cholesterol TINYINT,              -- 膽固醇水平（1: 正常, 2: 高於正常, 3: 高得多）
    gluc TINYINT,                     -- 血糖水平（1: 正常, 2: 高於正常, 3: 高得多）
    smoke TINYINT,                    -- 吸煙狀態（0: 非吸煙者, 1: 吸煙者）
    alco TINYINT,                     -- 酒精消費（0: 不消費, 1: 消費）
    active TINYINT,                   -- 身體活動狀態（0: 不活躍, 1: 活躍）
    cardio TINYINT,                   -- 心血管疾病狀態（0: 無, 1: 有）
    age_years INT,                  
    bmi DECIMAL(5,2),                 -- 身體質量指數（BMI）
    bp_category VARCHAR(50)           -- bp_category: Blood pressure category based on ap_hi and ap_lo. Categories include "Normal", "Elevated", "Hypertension Stage 1", "Hypertension Stage 2", and "Hypertensive Crisis".
);


LOAD DATA INFILE '/usr/local/mysql-files/FinalProject/cardio_data_processed.csv' -- 用的時候記得改路徑
INTO TABLE cardiovascular
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id, @dummy, gender, height, weight, @dummy, @dummy, cholesterol, gluc, smoke, alco, active, cardio, age_years, bmi, bp_category, @dummy);  -- 根據 CSV 中的欄位順序對應到 MySQL 表格的列