#!/usr/bin/env python3
"""
TabICLv2 vs XGBoost Benchmark — Imbalanced Classification
==========================================================

Ready-to-run benchmark comparing TabICLv2 (zero config) against XGBoost
(default params) on imbalanced data matching SocialPulse's positive rate
(~5% positive).

Usage:
    source tabicl_env/bin/activate
    python tabicl_benchmark.py

Requirements:
    pip install tabicl xgboost scikit-learn

Note: First TabICL run downloads the HF checkpoint (~minutes, one-time).
Note: On TARS Docker, pin numpy<2.3 (X86_V2 not supported by CPU).
"""

import time
import warnings
warnings.filterwarnings("ignore")

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

from tabicl import TabICLClassifier

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


def run_benchmark(n_samples=2000, n_features=20, positive_rate=0.05):
    """Run TabICL vs XGBoost on imbalanced synthetic data."""
    
    # Generate imbalanced dataset
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=12,
        n_redundant=5,
        weights=[1 - positive_rate, positive_rate],
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Dataset: {n_samples} samples, {n_features} features")
    print(f"Train: {len(y_train)} | Test: {len(y_test)}")
    print(f"Positive rate: {y.mean():.1%}")
    print()
    
    results = {}
    
    # --- TabICL ---
    print("=" * 50)
    print("TabICLv2 (zero config, CPU)")
    print("=" * 50)
    
    clf = TabICLClassifier(n_estimators=4, device="cpu")
    
    t0 = time.time()
    clf.fit(X_train, y_train)
    fit_time = time.time() - t0
    
    t0 = time.time()
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    pred_time = time.time() - t0
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    print(f"  Fit time:   {fit_time:.1f}s")
    print(f"  Predict:    {pred_time:.1f}s")
    print(f"  Accuracy:   {acc:.3f}")
    print(f"  ROC-AUC:    {auc:.3f}")
    print()
    print(classification_report(y_test, y_pred, target_names=["Negative", "Positive"]))
    
    results["tabicl"] = {"accuracy": acc, "roc_auc": auc, "fit_time": fit_time}
    
    # --- XGBoost baseline ---
    if HAS_XGB:
        print("=" * 50)
        print("XGBoost (default params)")
        print("=" * 50)
        
        xgb = XGBClassifier(n_estimators=100, eval_metric="logloss")
        
        t0 = time.time()
        xgb.fit(X_train, y_train)
        fit_time = time.time() - t0
        
        t0 = time.time()
        y_pred_xgb = xgb.predict(X_test)
        y_proba_xgb = xgb.predict_proba(X_test)[:, 1]
        pred_time = time.time() - t0
        
        acc_xgb = accuracy_score(y_test, y_pred_xgb)
        auc_xgb = roc_auc_score(y_test, y_proba_xgb)
        
        print(f"  Fit time:   {fit_time:.1f}s")
        print(f"  Predict:    {pred_time:.1f}s")
        print(f"  Accuracy:   {acc_xgb:.3f}")
        print(f"  ROC-AUC:    {auc_xgb:.3f}")
        print()
        print(classification_report(y_test, y_pred_xgb, target_names=["Negative", "Positive"]))
        
        results["xgboost"] = {"accuracy": acc_xgb, "roc_auc": auc_xgb, "fit_time": fit_time}
    
    # --- Summary ---
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"{'Model':<15} {'Accuracy':<12} {'ROC-AUC':<12} {'Fit (s)':<10}")
    print("-" * 49)
    for model, r in results.items():
        print(f"{model:<15} {r['accuracy']:<12.3f} {r['roc_auc']:<12.3f} {r['fit_time']:<10.1f}")
    
    return results


if __name__ == "__main__":
    run_benchmark()
