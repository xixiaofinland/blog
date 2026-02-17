# Classification

> Comparing to regression (predict values), classification has more areas to pay attention to.

In regression, the prediction target is a continuous value, and a single error metric often gives a decent first signal.  
In classification, model quality depends on decision boundaries, class balance, and threshold choices, so evaluation is usually the hard part.  
This thread uses MNIST to show not only how to train classifiers, but how to reason about whether their predictions are trustworthy.

---

## 1) MNIST dataset

**MNIST** is used because it's:

- easy to visualize,
- large enough to see realistic evaluation issues,
- naturally supports binary, multiclass, and beyond.

**Why this code matters:** We start with a controlled dataset so you can focus on evaluation logic instead of data cleaning noise.  
**What to look for:** The train/test split and shuffling are critical; without these, later metrics can be misleading.  
**Common trap:** Treating this split pattern as universal. In production, prefer stratified split and time-aware split when data is temporal.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml

mnist = fetch_openml("mnist_784", as_frame=False)
X, y = mnist.data, mnist.target.astype(np.uint8)

X_train, X_test = X[:60000], X[60000:]
y_train, y_test = y[:60000], y[60000:]

shuffle_idx = np.random.permutation(60000)
X_train, y_train = X_train[shuffle_idx], y_train[shuffle_idx]

def plot_digit(image_data):
    image = image_data.reshape(28, 28)
    plt.imshow(image, cmap="binary")
    plt.axis("off")

plot_digit(X[0])
plt.show()
```

---

## 2) Training a binary classifier (a “5-detector”)

- **positive class**: “is digit 5”
- **negative class**: “not 5”

**Why this code matters:** Binary classification is the simplest setting to learn precision/recall trade-offs.  
**What to look for:** `decision_function` gives a score for ranking confidence, while `predict` applies a default threshold to return True/False.  
**Common trap:** Reading decision scores as probabilities. They are margin-like scores, not calibrated probabilities.

```python
from sklearn.linear_model import SGDClassifier

y_train_5 = (y_train == 5)
y_test_5 = (y_test == 5)

sgd_clf = SGDClassifier(random_state=42)
sgd_clf.fit(X_train, y_train_5)

some_digit = X[0]
print("Prediction:", sgd_clf.predict([some_digit]))
print("Decision score:", sgd_clf.decision_function([some_digit]))
```
---

## 3) Performance measures: why accuracy can lie

**Why this code matters:** If only ~10% of images are digit 5, a naive model can get high accuracy by mostly predicting “not 5.”  
**What to look for:** Compare SGD accuracy against `DummyClassifier` baseline. If they are close, your model may not be useful.  
**Common trap:** Celebrating high accuracy without checking class distribution or baseline performance.

```python
from sklearn.model_selection import cross_val_score
from sklearn.dummy import DummyClassifier

print("SGD accuracy:",
      cross_val_score(sgd_clf, X_train, y_train_5, cv=3, scoring="accuracy"))

dummy_clf = DummyClassifier(strategy="most_frequent")
print("Dummy accuracy:",
      cross_val_score(dummy_clf, X_train, y_train_5, cv=3, scoring="accuracy"))
```
---

## 4) Confusion matrix

**Why this code matters:** The confusion matrix is the source of truth behind most classification metrics.  
**What to look for:**  
`TN`: correctly rejected non-5s, `FP`: wrongly flagged non-5s as 5, `FN`: missed real 5s, `TP`: correctly found 5s.  
**Common trap:** Looking only at diagonal totals without considering whether `FP` or `FN` is more costly in your use case.

```python
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix

y_train_pred = cross_val_predict(sgd_clf, X_train, y_train_5, cv=3)
confusion_matrix(y_train_5, y_train_pred)
```
---

## 5) Precision, recall, F1

**Why this code matters:** These metrics let you optimize for the failure mode that matters most.  
**What to look for:**  
High precision means fewer false alarms; high recall means fewer misses; F1 balances both when you need a single score.  
**Common trap:** Maximizing F1 by default. In many domains, one error type is far more expensive than the other.

```python
from sklearn.metrics import precision_score, recall_score, f1_score

precision = precision_score(y_train_5, y_train_pred)
recall = recall_score(y_train_5, y_train_pred)
f1 = f1_score(y_train_5, y_train_pred)

precision, recall, f1
```
---

## 6) Precision/Recall trade-off

**Why this code matters:** Classifiers output scores, and your threshold turns those scores into decisions.  
**What to look for:** As threshold increases, precision usually rises while recall falls. Pick threshold based on product/business cost.  
**Common trap:** Keeping threshold at default 0 without validating if it matches your required precision or recall target.

```python
from sklearn.metrics import precision_recall_curve

y_scores = cross_val_predict(
    sgd_clf, X_train, y_train_5,
    cv=3,
    method="decision_function"
)

precisions, recalls, thresholds = precision_recall_curve(
    y_train_5, y_scores
)

plt.plot(thresholds, precisions[:-1], label="precision")
plt.plot(thresholds, recalls[:-1], label="recall")
plt.legend()
plt.xlabel("threshold")
plt.grid(True)
plt.show()
```
---

## 7) ROC curve

**Why this code matters:** ROC summarizes ranking performance across all thresholds.  
**What to look for:** Curves closer to top-left and larger AUC indicate better separability than random guessing.  
**Common trap:** Using ROC alone on imbalanced data. Precision-Recall curves are often more informative when positives are rare.

```python
from sklearn.metrics import roc_curve, roc_auc_score

fpr, tpr, roc_thresholds = roc_curve(y_train_5, y_scores)
auc = roc_auc_score(y_train_5, y_scores)

plt.plot(fpr, tpr, label=f"SGD (AUC={auc:.4f})")
plt.plot([0, 1], [0, 1], "--", label="random")
plt.xlabel("FPR")
plt.ylabel("TPR")
plt.legend()
plt.grid(True)
plt.show()
```
---

## 8) Random Forest comparison

**Why this code matters:** Same task, different model family; this checks whether the issue is data-limited or model-limited.  
**What to look for:** Compare `auc` (SGD) vs `auc_forest`. Better AUC suggests better ranking quality over thresholds.  
**Common trap:** Comparing models using different validation setups. Keep CV split and metric consistent for fair comparison.

```python
from sklearn.ensemble import RandomForestClassifier

forest_clf = RandomForestClassifier(random_state=42, n_estimators=200)

y_probas_forest = cross_val_predict(
    forest_clf,
    X_train,
    y_train_5,
    cv=3,
    method="predict_proba"
)

y_scores_forest = y_probas_forest[:, 1]
auc_forest = roc_auc_score(y_train_5, y_scores_forest)

auc, auc_forest
```
---

## 9) Multiclass classification

**Why this code matters:** Real tasks often require choosing among many labels, not just yes/no.  
**What to look for:** Baseline multiclass accuracy vs scaled-pipeline accuracy; SGD usually benefits from feature scaling.  
**Common trap:** Forgetting to include preprocessing in the cross-validation pipeline, which causes leakage or inconsistent evaluation.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

sgd_clf_multi = SGDClassifier(random_state=42)
print("Multiclass accuracy:",
      cross_val_score(sgd_clf_multi, X_train, y_train,
                      cv=3, scoring="accuracy"))

sgd_scaled = make_pipeline(
    StandardScaler(),
    SGDClassifier(random_state=42, max_iter=100)
)

print("Scaled accuracy:",
      cross_val_score(sgd_scaled, X_train, y_train,
                      cv=3, scoring="accuracy"))
```
---

## 10) Error analysis

**Why this code matters:** A confusion matrix for multiclass reveals *where* the model struggles, not just *how much*.  
**What to look for:** Pairs of digits with high confusion (e.g., similar shapes). Those patterns guide targeted improvements.  
**Common trap:** Stopping at one aggregate score instead of diagnosing specific confusion pairs.

```python
from sklearn.metrics import ConfusionMatrixDisplay

y_train_pred_multi = cross_val_predict(
    sgd_scaled, X_train, y_train, cv=3
)

cm = confusion_matrix(y_train, y_train_pred_multi)
ConfusionMatrixDisplay(cm).plot(cmap="Blues")
plt.show()
```
---

## 11) Multilabel & Multioutput

### Multilabel

**Why this code matters:** One sample can have multiple valid labels (not mutually exclusive), which is common in tagging systems.  
**What to look for:** Output has multiple booleans per sample: here, `>=7` and `odd` are predicted together.  
**Common trap:** Treating multilabel as multiclass and forcing only one label per sample.

```python
from sklearn.neighbors import KNeighborsClassifier

y_train_large = (y_train >= 7)
y_train_odd = (y_train % 2 == 1)
y_multilabel = np.c_[y_train_large, y_train_odd]

knn_clf = KNeighborsClassifier()
knn_clf.fit(X_train, y_multilabel)

knn_clf.predict([some_digit])
```

### Multioutput (denoising)

**Why this code matters:** Multioutput predicts multiple targets at once; denoising predicts a whole clean pixel vector.  
**What to look for:** The predicted digit should preserve structure while removing injected random noise.  
**Common trap:** Assuming all classifiers support large multioutput targets efficiently; memory and latency can grow quickly.

```python
rng = np.random.RandomState(42)

noise = rng.randint(0, 100, (len(X_train), 784))
X_train_mod = X_train + noise
y_train_mod = X_train

knn_denoise = KNeighborsClassifier()
knn_denoise.fit(X_train_mod, y_train_mod)

clean_digit = knn_denoise.predict([X_train_mod[0]])

plot_digit(clean_digit[0])
plt.show()
```
---

## What we learned

Use this as a practical checklist:

1. Start with a simple binary slice to understand errors clearly.
2. Always compare against a naive baseline before trusting accuracy.
3. Inspect confusion matrix before optimizing any single metric.
4. Pick precision/recall target based on business cost of FP vs FN.
5. Tune threshold intentionally; default threshold is rarely optimal.
6. Compare model families under the same validation protocol.
7. For multiclass/multilabel tasks, diagnose per-label confusion, not just one aggregate score.

---

🔗 **Full runnable notebook:**

[▶ Run this notebook on Google Colab](https://colab.research.google.com/github/xixiaofinland/blog/blob/main/notebooks/classification.ipynb)
