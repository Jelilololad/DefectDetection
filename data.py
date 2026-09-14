import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N = 5000  # number of samples

def makedata():
    df = pd.DataFrame({
        "batch_id": np.random.randint(1000, 1100, N),
        "timestamp": pd.date_range("2026-01-01", periods=N, freq="min"),
        "operator_id": np.random.choice(["OP01", "OP02", "OP03", "OP04"], N),
        "temperature": np.random.normal(65, 5, N),
        "pressure": np.random.normal(3.2, 0.4, N),
        "speed": np.random.normal(1.5, 0.2, N),
        "humidity": np.random.normal(45, 10, N),
        "material_lot": np.random.choice(["LOT-A", "LOT-B", "LOT-C"], N),
    })

    df["defect"] = (
        (df["temperature"] > 72).astype(int)
        + (df["pressure"] < 2.8).astype(int)
        + (df["speed"] > 1.8).astype(int)
    )

    df["defect"] = (df["defect"] > 0).astype(int)

    data_dir = Path.cwd() / "data"
    data_dir.mkdir(exist_ok=True)

    data_path = data_dir / "data.csv"
    df.to_csv(data_path, index=False)

    print(f"CSV saved to: {data_path}")

    return df


if __name__ == "__main__":
    df = makedata()
    print(df.head())