# db_final_project

### 安裝套件
- pip install flask 
- pip install werkzeug 
- pip install python-dotenv 
- pip install scikit-learn 
- pip install mysql-connector-python 
- pip install pandas

### 需要更改程式碼的地方
- python: get_db_connection() 連到db的資料
- sql: 檔案路徑

### folder 說明
- dataset: 從kaggle上下載的dataset
  - https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-datasethttps://www.kaggle.com/datasets/rabieelkharoua/alzheimers-disease-dataset
  - https://www.kaggle.com/datasets/alexteboul/heart-disease-health-indicators-dataset/data
  - https://www.kaggle.com/datasets/colewelkins/cardiovascular-disease
  - https://www.kaggle.com/datasets/rabieelkharoua/alzheimers-disease-dataset
```bibtex
 @misc{rabie_el_kharoua_2024,
title={Alzheimer's Disease Dataset},
url={https://www.kaggle.com/dsv/8668279},
DOI={10.34740/KAGGLE/DSV/8668279},
publisher={Kaggle},
author={Rabie El Kharoua},
year={2024}
}
```
- sql: create table 的sql 檔案 (四個疾病)
  備註：table account and users are automatically created in main.py
- templates: html
- static/pictures: 搞耍

