import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


def load_and_preprocess(path):
    print(f"[INFO] Loading dataset from: {path}")
    df = pd.read_csv(path)
    print(f"[INFO] Dataset loaded: {df.shape}")

    # --- Drop irrelevant columns ---
    cols_to_drop = [
        "index", "LocationDesc", "TopicType", "TopicDesc",
        "Data_Value_Unit", "Data_Value_Type",
        "Data_Value_Footnote_Symbol", "Data_Value_Footnote",
        "Data_Value_Std_Err", "Low_Confidence_Limit", "High_Confidence_Limit",
        "GeoLocation", "TopicTypeId", "TopicId", "MeasureId",
        "StratificationID1", "StratificationID2", "StratificationID3", "StratificationID4",
        "SubMeasureID", "DisplayOrder"
    ]
    df.drop(columns=cols_to_drop, errors="ignore", inplace=True)
    print(f"[INFO] After dropping irrelevant columns: {df.shape}")

    # --- Handle missing values ---
    df.dropna(subset=["Data_Value"], inplace=True)
    print(f"[INFO] After dropping rows with missing Data_Value: {df.shape}")

    categorical_cols = ["LocationAbbr", "MeasureDesc", "DataSource", "Response",
                        "Gender", "Race", "Age", "Education"]
    for col in categorical_cols:
        if col in df.columns:
            df[col].fillna(df[col].mode()[0], inplace=True)

    if "Sample_Size" in df.columns:
        df["Sample_Size"].fillna(df["Sample_Size"].median(), inplace=True)

    # --- Normalize YEAR column (handle range strings like '2013-2014') ---
    if "YEAR" in df.columns:
        df["YEAR"] = df["YEAR"].astype(str).str.extract(r"(\d{4})")[0].astype(float)
        print(f"[INFO] YEAR column normalized. Sample values: {df['YEAR'].unique()[:5]}")

    # --- Create target label: Risk_Level ---
    median_val = df["Data_Value"].median()
    print(f"[INFO] Data_Value median (threshold): {median_val}")
    df["Risk_Level"] = (df["Data_Value"] > median_val).astype(int)
    df.drop(columns=["Data_Value"], inplace=True)
    print(f"[INFO] Risk_Level distribution:\n{df['Risk_Level'].value_counts()}")

    # --- Encode categorical columns ---
    le = LabelEncoder()
    for col in categorical_cols:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))
            print(f"[INFO] Encoded column: {col}")

    # --- Scale numerical columns ---
    num_cols = [c for c in ["YEAR", "Sample_Size"] if c in df.columns]
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    print(f"[INFO] Scaled numerical columns: {num_cols}")

    print("[INFO] Preprocessing complete.")
    return df


if __name__ == "__main__":
    output_dir = "preprocessing/tobacco_preprocessed"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "preprocessed.csv")
    df_ready = load_and_preprocess("data/rows.csv")
    df_ready.to_csv(output_path, index=False)
    print(f"[INFO] Preprocessed file saved to: {output_path}")
