CREATE TABLE alzheimers (
    PatientID INT PRIMARY KEY,          -- 病患編號，主鍵
    Age INT,                            -- 年齡
    Gender TINYINT,                 -- 性別
    Ethnicity TINYINT,              -- 種族
    EducationLevel TINYINT,         -- 教育程度
    BMI FLOAT,                          -- BMI 值
    Smoking TINYINT,                -- 是否吸菸
    AlcoholConsumption FLOAT,     -- 酒精消耗
    PhysicalActivity FLOAT,       -- 身體活動
    DietQuality FLOAT,            -- 飲食品質
    SleepQuality FLOAT,
    FamilyHistoryAlzheimers TINYINT,
    CardiovascularDisease FLOAT,
    Diabetes FLOAT,
    Depression TINYINT,
    DeadInjury TINYINT,
    Hypertension TINYINT
);

LOAD DATA INFILE '/mnt/c/Users/judy7/OneDrive/Desktop/Sophomore/db/final_project_code/alzheimers_disease_data.csv' -- 記得替換為實際檔案路徑
INTO TABLE patients
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(PatientID, Age, Gender, Ethnicity, EducationLevel, BMI, Smoking, AlcoholConsumption, PhysicalActivity, DietQuality, @SleepQuality, @FamilyHistoryAlzheimers, @CardiovascularDisease, @Diabetes, @Depression, @HeadInjury, @Hypertension, @SystolicBP, @DiastolicBP, @CholesterolTotal, @CholesterolLDL, @CholesterolHDL, @CholesterolTriglycerides, @MMSE, @FunctionalAssessment, @MemoryComplaints, @BehavioralProblems, @ADL, @Confusion, @Disorientation, @PersonalityChanges, @DifficultyCompletingTasks, @Forgetfulness, @Diagnosis, @DoctorInCharge)
WHERE Diagnosis = 1;
