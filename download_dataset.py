from pathlib import Path

from datasets import load_dataset

DATASET_NAME = "LorthGyu/indonesian-tourism"
RAW_PATH = Path("data/raw/indonesian_tourism.csv")


def main() -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(DATASET_NAME)
    df = dataset["train"].to_pandas()
    total_rows = len(df)
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)
    df.to_csv(RAW_PATH, index=False)

    print("Dataset berhasil didownload dari Hugging Face.")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Jumlah data train: {total_rows}")
    print(f"Jumlah data unik berdasarkan id: {len(df)}")
    print(f"File tersimpan: {RAW_PATH}")


if __name__ == "__main__":
    main()
