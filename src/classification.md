# Classification

> Comparing to regression (predict values), classification has more areas to pay attention to.

---

## 1) MNIST dataset

**MNIST** is used because it's:

- easy to visualize,
- large enough to see realistic evaluation issues,
- naturally supports binary, multiclass, and beyond.

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

```python
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix

y_train_pred = cross_val_predict(sgd_clf, X_train, y_train_5, cv=3)
confusion_matrix(y_train_5, y_train_pred)
```
---

## 5) Precision, recall, F1

```python
from sklearn.metrics import precision_score, recall_score, f1_score

precision = precision_score(y_train_5, y_train_pred)
recall = recall_score(y_train_5, y_train_pred)
f1 = f1_score(y_train_5, y_train_pred)

precision, recall, f1
```
---

## 6) Precision/Recall trade-off

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

1. Accuracy is not enough (especially with imbalance).
2. Confusion matrix is foundational.
3. Precision/recall define different trade-offs.
4. Threshold selection matters.
5. PR and ROC curves guide operating points.
6. Multiclass strategies are standard.
7. Error analysis drives improvement.

---

🔗 **Full runnable notebook:**

[▶ Run this notebook on Google Colab](https://colab.research.google.com/github/xixiaofinland/blog/blob/main/notebooks/classification.ipynb)

