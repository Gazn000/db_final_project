from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from sqlalchemy import create_engine
import pandas as pd

# MySQL 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "gazn",
    "password": "nycu112550141",
    "database": "final_project"
}

# 创建 SQLAlchemy 数据库引擎
def create_engine_connection():
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_string)
    return engine

# 获取数据的函数
def get_training_data():
    engine = create_engine_connection()
    query = """
    SELECT age_years, gender, bmi, smoke, alco, active, 
           gluc, cholesterol, bp_category, cardio
    FROM cardiovascular;
    """
    data = pd.read_sql(query, engine)  # 使用 SQLAlchemy 引擎
    return data


# 加载数据
data = get_training_data()

# 处理数据
data['bp_category'] = data['bp_category'].map({
    'Normal': 1,
    'Elevated': 2,
    'Hypertension Stage 1': 3,
    'Hypertension Stage 2': 4
})
data = data.fillna(0)  # 填补缺失值

# 分离特征和目标
X = data[['age_years', 'gender', 'bmi', 'smoke', 'alco', 'active', 'gluc', 'cholesterol', 'bp_category']]
y = data['cardio']

# 分割训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 标准化特征
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

## 定义模型
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "Linear SVM": CalibratedClassifierCV(LinearSVC(max_iter=10000, random_state=42)), 
    "K-Nearest Neighbors (KNN)": KNeighborsClassifier(n_neighbors=5)        # 可暂时移除
}

# 模型训练和评估
results = []

for name, model in models.items():
    print(f"Training model: {name}")
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, "predict_proba") else None

    report = classification_report(y_test, y_pred, output_dict=True)
    roc_auc = roc_auc_score(y_test, y_proba) if y_proba is not None else "N/A"

    results.append({
        "Model": name,
        "Accuracy": report['accuracy'],
        "Precision": report['1']['precision'],
        "Recall": report['1']['recall'],
        "F1-Score": report['1']['f1-score'],
        "ROC-AUC": roc_auc
    })
    print(f"Completed model: {name}")

# 转换为 DataFrame 展示结果
results_df = pd.DataFrame(results)
print(results_df)

'''
                       Model  Accuracy  Precision    Recall  F1-Score   ROC-AUC
0        Logistic Regression  0.690646   0.686050  0.684414  0.685231  0.747481
1              Random Forest  0.643974   0.641046  0.627992  0.634452  0.697283
2          Gradient Boosting  0.702229   0.724825  0.636337  0.677704  0.762059
3                 Linear SVM  0.690206   0.685510  0.684216  0.684862  0.747049
4  K-Nearest Neighbors (KNN)  0.657756   0.656327  0.638919  0.647506  0.703154
'''