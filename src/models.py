import pandas as pd
from pathlib import Path
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import GridSearchCV, train_test_split
import pickle
import json
from sklearn.metrics import log_loss, roc_auc_score
from src.data import makedata
from lightgbm import LGBMClassifier


def data_wrangling():

    df = pd.read_csv("src/data/data.csv")

    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    for col in df.select_dtypes("object").columns:
        categories = sorted(df[col].unique())
        mapping = {v: i for i, v in enumerate(categories)}
        df[col] = df[col].map(mapping)

    X = df.drop(columns=["defect"])
    y = df["defect"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):

    pipe = Pipeline([
        ("scaler", RobustScaler()),
        ("smote", SMOTE(random_state=42)),
        ("model", LGBMClassifier(
            objective="binary",
            random_state=42,
            verbosity=-1
        ))
    ])

    params = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [3, 4, 5],
        "model__num_leaves": [15, 31],
        "model__learning_rate": [0.05, 0.1]
    }

    grid = GridSearchCV(
        pipe,
        param_grid=params,
        cv=5,
        n_jobs=-1,
        verbose=1
    )

    grid.fit(X_train, y_train)

    return grid.best_estimator_, grid


def model_performance(best_model, X_test, y_test, grid):

    y_pred_proba = best_model.predict_proba(X_test)[:, 1]

    ll = log_loss(y_test, y_pred_proba)
    auc = roc_auc_score(y_test, y_pred_proba)

    return grid.best_score_, grid.best_params_, ll, auc


def save_model(best_model, metrics):

    model_dir = Path.cwd() / "artifacts"
    model_dir.mkdir(exist_ok=True)

    model_path = model_dir / "model.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)

    metrics_path = model_dir / "metrics.json"

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    return model_path, metrics_path


def mains():

    file_path = Path("src/data/data.csv")

    if not file_path.exists():
        print("Data does not exist. Run data.py first.")
        print("Running Data File")
        data = makedata()
        
    X_train, X_test, y_train, y_test = data_wrangling()

    best_model, grid = train_model(X_train, y_train)

    best_score, best_params, ll, auc = model_performance(best_model, X_test, y_test, grid)

    model_params = best_model.named_steps["model"].get_params()

    metrics = {
        "model_parameters": model_params,
        "best_score": best_score,
        "best_params": best_params,
        "log_loss": ll,
        "AUC": auc
    }

    model_path, metrics_path = save_model(best_model, metrics)

    print(f"Model saved to: {model_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"best_score: {best_score:.4f}")
    print(f"best_params: {best_params}")
    print(f"Log Loss: {ll:.4f}")
    print(f"AUC: {auc:.4f}")


if __name__ == "__main__":
    mains()
