"""Train a simple model that predicts whether a test will fail based on report data.

This script is intentionally minimal and framework-agnostic: it uses the
pluggable extractor from `ai.healing.report_analyzer` to obtain per-test
messages, computes simple numeric features, and trains a RandomForest
classifier. The resulting model is stored with joblib and can be used by
other modules.

Usage examples:
  # Train on a single Playwright JSON report
  python ai/train_model.py --report reports/report.json --output ai/models/model.pkl

  # Train using sample report provided with the repo
  python ai/train_model.py --report ai/data/sample_report.json --output ai/models/sample_model.pkl

This script requires scikit-learn and pandas (listed in requirements.txt).
"""
import argparse
import os
import json
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

from ai.healing import report_analyzer as ra


def extract_features(parsed_report: Any) -> List[Dict]:
    """Return a list of feature dicts, one per test case found in the report."""
    rows = []
    # select extractor
    extractor = ra.default_playwright_extractor if isinstance(parsed_report, dict) else ra.junit_xml_extractor
    for suite, test_title, messages in extractor(parsed_report):
        num_errors = len(messages)
        total_len = sum(len(m or '') for m in messages)
        # count by matcher types
        counts = {}
        for _, err_type, _ in ra.DEFAULT_MATCHERS:
            counts[err_type] = 0
        others = 0
        for m in messages:
            matched = False
            for pattern, err_type, _ in ra.DEFAULT_MATCHERS:
                if pattern.search((m or '')):
                    counts[err_type] += 1
                    matched = True
                    break
            if not matched:
                others += 1

        row = {
            'suite': suite,
            'test_title': test_title,
            'num_errors': num_errors,
            'total_msg_len': total_len,
            'others': others,
        }
        row.update(counts)
        # label: failed if any error present
        row['failed'] = 1 if num_errors > 0 else 0
        rows.append(row)
    return rows


def load_parsed(path: str):
    return ra.load_report(path=path)


def train(features: pd.DataFrame, output_path: str, test_size: float = 0.2, random_state: int = 42):
    X = features.drop(columns=['suite', 'test_title', 'failed'])
    y = features['failed']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    clf = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print('\nModel evaluation:')
    print(classification_report(y_test, preds))

    # ensure output dir
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    joblib.dump(clf, output_path)
    print(f'Wrote model to {output_path}')


def main():
    parser = argparse.ArgumentParser(description='Train a small failure-prediction model from test reports')
    parser.add_argument('--report', required=True, help='Path to a test report (JSON or XML)')
    parser.add_argument('--output', default='ai/models/model.pkl', help='Path to write the trained model')
    parser.add_argument('--test-size', type=float, default=0.2)
    parser.add_argument('--random-state', type=int, default=42)
    args = parser.parse_args()

    print(f'Loading report: {args.report}')
    parsed = load_parsed(args.report)
    if parsed is None:
        print('No report data found or failed to parse. Exiting.')
        return

    rows = extract_features(parsed)
    if not rows:
        print('No test cases found in the report. Nothing to train.')
        return

    df = pd.DataFrame(rows)
    # drop identifier columns and ensure numeric
    df_numeric = df.copy()
    df_numeric.fillna(0, inplace=True)
    numeric_cols = [c for c in df_numeric.columns if c not in ('suite', 'test_title')]
    df_numeric[numeric_cols] = df_numeric[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    train(df_numeric, args.output, test_size=args.test_size, random_state=args.random_state)


if __name__ == '__main__':
    main()
