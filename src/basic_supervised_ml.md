# Notes on Machine Learning Specialization – Chapter 1

This post summarizes my takeaways from the **first chapter** of the [Machine Learning Specialization](https://www.deeplearning.ai/courses/machine-learning-specialization/).
It covers the basics of linear regression, gradient descent, logistic regression, and the problem of overfitting.

---

## 1. Linear Regression

- **Goal**: Predict a continuous value (like house price).
- **Model**: Draw a straight line that best fits the training data.
- **Parameters**:
  - Weight (slope): how steep the line is.
  - Bias (intercept): where the line crosses the y-axis.
- **Task**: Adjust these parameters so predictions are close to the actual values.

---

## 2. Gradient Descent in Practice

- **Cost function**: Measures how far predictions are from actual results.
- **Idea**: Start with random parameters, then repeatedly adjust them to reduce the cost.
- **Learning rate**: Controls the step size.
  - Too big → model may jump around and never settle.
  - Too small → training becomes very slow.

---

## 3. Cost Function vs Loss Function

- **Loss function**: Error for one training example.
- **Cost function**: Average error across all examples.

Think of it like this: loss = “how wrong am I on this one?”, cost = “how wrong am I overall?”.

---

## 4. Logistic Regression (Classification)

- **Goal**: Predict categories (like spam vs not spam).
- **Model**: Instead of a line, use the **sigmoid function** to squash predictions between 0 and 1.
- **Output**: A probability. Example: 0.9 → very likely spam.
- **Decision rule**: If probability ≥ 0.5 → class 1, else → class 0.

---

## 5. Cost Function for Logistic Regression

- Using squared error (like in linear regression) doesn’t work well here.
- Instead, we use **log loss (cross-entropy)**, which:
  - Punishes confident but wrong predictions more.
  - Encourages probabilities that match reality.

---

## 6. Gradient Descent for Logistic Regression

- Same process as before:
  1. Compute predictions.
  2. Compare with actual results.
  3. Adjust parameters to reduce log loss.

Because the sigmoid is smooth and differentiable, gradient descent works well.

---

## 7. Overfitting

- **What it is**: The model memorizes training data but performs poorly on new data.
- **Signs**:
  - Training error is very low.
  - Test error is high.
- **Fixes**:
  - Get more data.
  - Use regularization (penalize overly complex models).
  - Simplify the model.

---

## Final Thoughts

This chapter gave me the foundations of supervised learning:
- Linear vs logistic regression.
- Gradient descent as the optimization engine.
- Why the right cost function matters.
- Early warning signs of overfitting.

Next, I’ll move on to regularization and more advanced techniques.

