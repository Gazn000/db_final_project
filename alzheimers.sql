CREATE TABLE alzheimers_diagnosed (
    PatientID INT PRIMARY KEY,
    Age INT,
    Gender TINYINT,
    Ethnicity TINYINT,
    EducationLevel TINYINT,
    BMI FLOAT,
    Smoking TINYINT,
    AlcoholConsumption FLOAT,
    PhysicalActivity FLOAT,
    DietQuality FLOAT,
    SleepQuality FLOAT,
    FamilyHistoryAlzheimers TINYINT,
    CardiovascularDisease FLOAT,
    Diabetes FLOAT,
    Depression TINYINT,
    HeadInjury TINYINT,
    Hypertension TINYINT,
    Diagnosis TINYINT,
    MMSE INT
);


-- Step 1: 加載數據到中間表
CREATE TABLE alzheimers_raw LIKE alzheimers_diagnosed;

LOAD DATA INFILE '/mnt/c/Users/judy7/OneDrive/Desktop/Sophomore/db/final_project_code/alzheimers_disease_data.csv'
INTO TABLE alzheimers_raw
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(PatientID, Age, Gender, Ethnicity, EducationLevel, BMI, Smoking, AlcoholConsumption, PhysicalActivity, DietQuality, SleepQuality, FamilyHistoryAlzheimers, @CardiovascularDisease, @Diabetes, Depression, HeadInjury, Hypertension, @SystolicBP, @DiastolicBP, @CholesterolTotal, @CholesterolLDL, @CholesterolHDL, @CholesterolTriglycerides, MMSE, @FunctionalAssessment, @MemoryComplaints, @BehavioralProblems, @ADL, @Confusion, @Disorientation, @PersonalityChanges, @DifficultyCompletingTasks, @Forgetfulness, Diagnosis, @DoctorInCharge);

-- Step 2: 篩選數據到診斷表
INSERT INTO alzheimers_diagnosed
SELECT * 
FROM alzheimers_raw
WHERE Diagnosis = 1;
