import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

st.title("🛒  Association Rules Explorer")

file = st.file_uploader("Upload CSV or Excel with transactions (comma-separated)", type=None)

if file:
    if file.name.endswith(".csv"):
        raw_data = pd.read_csv(file)
    else:
        raw_data = pd.read_excel(file)

    st.write("📥 Uploaded Data", raw_data)

    if st.checkbox("🪓SPLIT DATAt"):
                # Select column to split
        col = st.selectbox("Select column with names (e.g. A;B;C)", raw_data.columns)
        st.write(col.split(';'))
        
        
        # Let user choose or enter separator
        sep_option = st.selectbox("Choose a separator", [",", ";", "|", "Tab", "Space", "Custom"])
        if sep_option == "Tab":
            sep = "\t"
        elif sep_option == "Space":
            sep = " "
        elif sep_option == "Custom":
            sep = st.text_input("Enter custom separator", value=",")
        else:
            sep = sep_option

        # Perform split
        data_split = raw_data[col].astype(str).str.split(sep, expand=True)


        #data_split.columns = [f"Item {i+1}" for i in range(data_split.shape[1])]
        data_split.columns = [f"{col}_part_{i+1}" for i in range(data_split.shape[1])]

        
        raw_data = pd.concat([raw_data,data_split], axis=1)
        raw_data.drop(columns=col,inplace = True)

        st.write(raw_data)

   # # Convert to list of lists
    #transactions = data.iloc[:, 0].dropna().apply(lambda x: [item.strip() for item in str(x).split(',')])



    with st.sidebar:
            st.header("⚙️ Parameters")
            use_encoder = st.checkbox("Use TransactionEncoder", value=True)
            support = st.slider("Min Support", 0.01, 1.0, 0.2, 0.01)
            confidence = st.slider("Min Confidence", 0.01, 1.0, 0.5, 0.01)
            lift = st.slider("Min Lift", 0.5, 5.0, 1.0, 0.1)

        # 🔁 Process data based on user input
    if use_encoder:
        transactions = raw_data.astype(str).values.tolist()
        transactions = [[item.strip() for item in row if pd.notna(item) and item.strip() != ""] for row in transactions]

        te = TransactionEncoder()
        te_data = te.fit(transactions).transform(transactions)
        data = pd.DataFrame(te_data, columns=te.columns_)
    else:
        data = raw_data.copy()
        # Convert any '1'/'0' strings or non-boolean values to 1/0 integers
        data = data.applymap(lambda x: 1 if str(x).strip().lower() in ["1", "true"] else 0)

  # 📌 Frequent Itemsets
    frequent_itemsets = apriori(data, min_support=support, use_colnames=True)
    st.subheader("🧮 Frequent Itemsets")

    if frequent_itemsets.empty:
        st.warning("No frequent itemsets found. Try lowering the minimum support.")
    else:
        frequent_itemsets["itemsets_str"] = frequent_itemsets["itemsets"].apply(lambda x: ', '.join(sorted(list(x))))
        st.dataframe(frequent_itemsets[["itemsets_str", "support"]])

        valid_itemsets = frequent_itemsets[frequent_itemsets["itemsets"].apply(lambda x: len(x) >= 2)]

        if valid_itemsets.empty:
            st.warning("No association rules can be generated because there are no itemsets with 2 or more items.")
        else:
            try:
                rules = association_rules(frequent_itemsets, metric="lift", min_threshold=lift, support_only=False)
                rules = rules[rules["confidence"] >= confidence]

                st.subheader("📈 Association Rules")

                if rules.empty:
                    st.warning("No rules found. Try lowering the confidence or lift thresholds.")
                else:
                    rules["antecedents"] = rules["antecedents"].apply(lambda x: ', '.join(sorted(list(x))))
                    rules["consequents"] = rules["consequents"].apply(lambda x: ', '.join(sorted(list(x))))
                    st.dataframe(rules[["antecedents", "consequents", "support", "confidence", "lift"]])
                # Plotting

                    # ---------------------------
                    # 🎨 Plotting Top 10 Rules by Confidence
                    # ---------------------------
                try:
                    st.subheader("📊 Top 10 Rules by Support, Confidence & Lift")

                    metrics = ["support", "confidence", "lift"]
                    titles = ["Top 10 Rules by Support", "Top 10 Rules by Confidence", "Top 10 Rules by Lift"]
                    palettes = ["Blues", "crest", "mako"]

                      # Create 3 Streamlit columns

                    for i, metric in enumerate(metrics):
                        top_rules = rules.sort_values(metric, ascending=False).head(10)
                        labels = top_rules["antecedents"].astype(str) + " → " + top_rules["consequents"].astype(str)

                        fig, ax = plt.subplots(figsize=(8, 10))  # Larger vertical plots

                        sns.barplot(
                            x=top_rules[metric],
                            y=labels,
                            palette=palettes[i],
                            ax=ax
                        )

                        ax.set_title(titles[i], fontsize=16)
                        ax.set_xlabel(metric.capitalize(), fontsize=14)
                        ax.set_ylabel("Rule", fontsize=14)

                        for bar in ax.patches:
                            width = bar.get_width()
                            ax.text(width + 0.01, bar.get_y() + bar.get_height() / 2,
                                    f"{width:.2f}", va='center', fontsize=11)

                        st.pyplot(fig)
                        plt.clf()

                except Exception as e:
                    st.error(f"An error occurred while plotting metrics: {e}")


            except KeyError as e:
                st.error(f"Error generating rules: {e}. Try setting `support_only=True` or check input data.")
