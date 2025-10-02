# Linear and Logistic Regression

This post summarizes my takeaways from the **first chapter** of the [Machine
Learning
Specialization](https://www.deeplearning.ai/courses/machine-learning-specialization/).

It covers the basics of linear regression, gradient descent, logistic
regression, and the problem of overfitting. More importantly, I’ll focus on why
we use these ideas, what they solve, and how they fit together.

## Linear Regression

**What it does?**

Given historic data, it predicts new values (like house price, car mileage, or
sales revenue). Instead of guessing outcomes, linear regression provides a
systematic way to estimate them from data.

**How to find the best fit LR model in practice?**

There are two main challenges:

1. **Choosing the right model form** – deciding what features (and
   transformations of features) to include.

2. **Finding the best parameters** – estimating the weights associated with
   those features.

The **second problem** is straightforward. Algorithms like gradient descent can
find the optimal parameters. Given a fixed model, this process is deterministic
and guarantees the best weights.

The **first problem** is much harder. No algorithm can directly tell you the
“correct” polynomial degree, transformations, or feature interactions. This is a
model selection problem, not just an optimization one. It requires exploration
and judgment.

Feature engineering is often considered an art because it involves:

- Domain expertise
- Experimentation
- Iterative refinement
- Human judgment

In this course, the focus is primarily on the second challenge, introducing
**Gradient Descent** as a way to optimize parameters.

Gradient Descent, Loss Function, and Cost Function
- **Loss function**: The error for a single training example (“How wrong am I
  here?”).
- **Cost function**: The average error across the whole dataset (“How wrong am I
  overall?”).

Gradient descent works by repeatedly adjusting parameters to reduce the cost
function.

Because gradient descent must loop through potentially millions (or billions) of
features — especially in large-scale models like LLMs — computation speed
becomes critical. This is why GPU acceleration plays a pivotal role in modern
machine learning: it dramatically speeds up these large-scale calculations.

## Logistic Regression (Classification)

**What it does?**

While linear regression predicts continuous values, logistic regression is used
for **classification tasks** — predicting categories such as spam vs. not spam,
disease vs. no disease, etc.

Instead of fitting a straight line, logistic regression uses the **sigmoid
function** to squeeze predictions into a range between 0 and 1.

- Output: A probability. Example: 0.9 → very likely spam.
- Decision rule: If probability ≥ 0.5 → predict class 1, otherwise class 0.

**Cost Function for Logistic Regression**

Squared error (used in linear regression) doesn’t work well for classification
because it doesn’t handle probabilities properly.

Instead, logistic regression uses log loss (cross-entropy loss):

- Penalizes confident but wrong predictions much more heavily.
- Rewards probabilities that better reflect reality.

This ensures the model doesn’t just guess classes, but actually learns
meaningful probabilities.

**Overfitting**

When a model memorizes training data instead of learning general patterns. It
performs great on training data but poorly on unseen data.

Common fixes:

- Add more data when possible
- Apply regularization (penalize overly complex models).
- Simplify the model structure (loop back to the first challenge mentioned
  earlier)

## Final Thoughts

This chapter laid the groundwork for supervised learning:

- Linear regression for continuous values vs. logistic regression for
  categories.
- Gradient descent as the universal optimization method.
- Why the right cost function matters.
- How to spot and address overfitting early.
