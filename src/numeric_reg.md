# End-to-End Regression with scikit-learn (Numeric Features Only)

This chapter demonstrates a complete regression workflow using **scikit-learn** and the **California Housing dataset**.
All features in this dataset are numeric, which allows us to focus on the core machine learning pipeline without introducing categorical preprocessing.

The goal is not to optimize performance aggressively, but to build a **correct, leak-free, and reproducible workflow**.

---

## Load the Dataset

We load the California Housing dataset directly from scikit-learn.
It contains 8 numeric features and one numeric target variable, `MedHouseVal`.

```python
data = fetch_california_housing(as_frame=True)
df = data.frame.copy()

target_col = "MedHouseVal"
df.head()
```

---

## Train / Test Split

We split the dataset into training and test sets **before any preprocessing**.
The test set is treated as *hands-off* until the final evaluation to prevent data leakage.

```python
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42
)

train_df.shape, test_df.shape
```

---

## Separate Features and Target

We separate input features (`X`) from the target variable (`y`) for both training and test data.

```python
X_train = train_df.drop(columns=[target_col])
y_train = train_df[target_col].copy()

X_test = test_df.drop(columns=[target_col])
y_test = test_df[target_col].copy()
```

---

## Numeric Feature Preprocessing

All features in this dataset are numeric.
We explicitly list the numeric columns and define a preprocessing pipeline that:

- imputes missing values using the median
- standardizes features using `StandardScaler`

```python
num_cols = list(X_train.columns)
num_cols
```

```python
numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
```

---

## Build the Full Pipeline

We choose a `RandomForestRegressor` as the model and combine it with the preprocessing pipeline.
Keeping preprocessing and modeling inside a single pipeline ensures consistency across training and evaluation.

```python
model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

pipe = Pipeline(steps=[
    ("prep", numeric_pipeline),
    ("model", model),
])

print(pipe)
```

---

## Cross-Validation on the Training Set

Before touching the test set, we estimate performance using **5-fold cross-validation** on the training data.
We use **RMSE (Root Mean Squared Error)** as the evaluation metric.

```python
scores = cross_val_score(
    pipe,
    X_train,
    y_train,
    scoring="neg_root_mean_squared_error",
    cv=5
)

rmse = -scores
rmse.mean(), rmse.std()
```

---

## Final Evaluation on the Test Set

After cross-validation, we fit the pipeline on the full training set and evaluate once on the test set.
This provides an unbiased estimate of generalization performance.

```python
pipe.fit(X_train, y_train)

y_pred = pipe.predict(X_test)
test_rmse = root_mean_squared_error(y_test, y_pred)

test_rmse
```

---

## Interpretation

The final test RMSE is approximately **0.50**.

Since the target variable is measured in **hundreds of thousands of dollars**, this corresponds to an average prediction error of roughly **$50,000**.

This result is realistic for this dataset and confirms that the workflow is functioning correctly.

---

## Summary

In this chapter we:

- split the data before preprocessing to avoid leakage
- built a numeric-only preprocessing pipeline
- combined preprocessing and modeling using `Pipeline`
- evaluated using cross-validation and a final test set

This structure serves as a clean foundation for future extensions, such as handling categorical features or experimenting with other models.

---

## Reproducibility

- Python ≥ 3.10
- scikit-learn ≥ 1.6.1
- Fixed random seed (`random_state=42`)

---

🔗 **Full runnable notebook:**

[▶ Run this notebook on Google Colab](https://colab.research.google.com/github/xixiaofinland/blog/blob/main/notebooks/numeric_regression.ipynb)

