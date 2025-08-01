# 🛒 Association Rules Explorer App

This interactive **Streamlit app** helps you discover meaningful association rules from transactional data using the **Apriori algorithm**. It allows users to upload datasets, configure thresholds (support, confidence, lift), and visualize the top rules in clean bar plots.

---

## 🚀 Features

- 📁 Upload transactional datasets (CSV or Excel)
- ✅ Automatically converts transactions to one-hot encoded format
- 🧮 Generates frequent itemsets with customizable **minimum support**
- 🔗 Derives association rules based on **confidence** and **lift thresholds**
- 📊 Visualizes **Top 10 Rules** by:
  - Support
  - Confidence
  - Lift
- 🎨 Enhanced with Seaborn and Matplotlib barplots
- 📝 Displays exact rule metrics next to each bar

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/association-rules-app.git
cd association-rules-app
