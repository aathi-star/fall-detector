import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib

from utils import extract_features, ensure_dirs

SR = 25
WIN_SAMPLES = SR * 1  # 1 second windows


def generate_normal() -> pd.DataFrame:
    ax = np.random.normal(0, 0.1, WIN_SAMPLES)
    ay = np.random.normal(0, 0.1, WIN_SAMPLES)
    az = np.random.normal(9.81, 0.1, WIN_SAMPLES)
    return pd.DataFrame({'ax': ax, 'ay': ay, 'az': az})


def generate_fall() -> pd.DataFrame:
    ax = np.random.normal(0, 0.2, WIN_SAMPLES)
    ay = np.random.normal(0, 0.2, WIN_SAMPLES)
    az = np.random.normal(9.81, 0.2, WIN_SAMPLES)
    idx = np.random.randint(WIN_SAMPLES // 4, WIN_SAMPLES // 2)
    ax[idx:idx + 2] += np.random.normal(0, 4, 2)
    ay[idx:idx + 2] += np.random.normal(0, 4, 2)
    az[idx:idx + 2] -= np.random.uniform(9, 12)
    return pd.DataFrame({'ax': ax, 'ay': ay, 'az': az})


def main():
    features = []
    labels = []
    for _ in range(100):
        features.append(extract_features(generate_normal()))
        labels.append('Normal')
    for _ in range(100):
        features.append(extract_features(generate_fall()))
        labels.append('Fall')

    X = pd.DataFrame(features)
    y = np.array(labels)

    model = make_pipeline(
        StandardScaler(),
        SVC(probability=True, class_weight='balanced')
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring='f1')
    print(f'F1 score: {scores.mean():.3f} ± {scores.std():.3f}')

    model.fit(X, y)
    ensure_dirs('models')
    joblib.dump(model, 'models/fall_detector.joblib')
    print('Model saved to models/fall_detector.joblib')


if __name__ == '__main__':
    main()
