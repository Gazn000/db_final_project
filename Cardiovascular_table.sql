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


LOAD DATA INFILE '/mnt/c/Users/judy7/OneDrive/Desktop/Sophomore/db/final_project_code/cardio_data_processed.csv' -- 用的時候記得改路徑
INTO TABLE cardiovascular
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id, gender, height, weight, @ap_hi, @ap_lo, cholesterol, gluc, smoke, alco, active, cardio, age_years, bmi, bp_category, @bp_category_encoded);  -- 根據 CSV 中的欄位順序對應到 MySQL 表格的列
