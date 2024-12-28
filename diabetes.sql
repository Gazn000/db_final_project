CREATE TABLE diabetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    HighBP TINYINT,                   -- 血壓水平（（0:正常 1:高血壓 ）
    HighChol TINYINT,                 -- 膽固醇水平（0:正常 1:高膽固醇 ）
    BMI DECIMAL(5,2),                 -- 身體質量指數（BMI）
    Smoker TINYINT,                   -- 吸煙狀態（0: 非吸煙者, 1: 吸煙者）
    Stroke TINYINT,                   -- 中風(0:無 1:有)
    Diabetes_binary TINYINT,     -- 心血管疾病狀態（0: 無, 1: 有）
    PhysActivity TINYINT,             -- 身體活動狀態（0: 不活躍, 1: 活躍）
    HvyAlcoholConsump TINYINT,        -- 酒精消費（0: 不消費, 1: 消費）
    Sex TINYINT,                      -- 性別(0:female 1:male)
    Age TINYINT                 
);

LOAD DATA INFILE '/mnt/c/Users/judy7/OneDrive/Desktop/Sophomore/db/final_project_code/diabetes_binary_5050split_health_indicators_BRFSS2015.csv' -- 用的時候記得改路徑
INTO TABLE diabetes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Diabetes_binary, HighBP, HighChol, @dummy, BMI, Smoker, Stroke, @HeartDiseaseorAttack, PhysActivity, @dummy, @dummy,HvyAlcoholConsump, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, Sex, Age, @dummy, @dummy);  -- 根據 CSV 中的欄位順序對應到 MySQL 表格的列

