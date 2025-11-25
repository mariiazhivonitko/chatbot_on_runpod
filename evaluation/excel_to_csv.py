import pandas as pd
import re

# Precompile regex patterns for speed
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F\x7F-\x9F]")

def clean_text(text):
    if not isinstance(text, str):
        return text

    # Normalize quotation marks and apostrophes
    text = (text
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("\xa0", " ")
            .replace("\ufeff", "")
    )

    # Remove control characters
    text = CONTROL_CHARS_RE.sub("", text)

    # Strip whitespace
    return text.strip()


def excel_to_clean_csv(input_excel_path: str, output_csv_path: str, sheet_name=0):
    # Load Excel
    df = pd.read_excel(input_excel_path, sheet_name=sheet_name)

    # Drop fully empty rows/columns early
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # Clean column names
    df.rename(columns=lambda col: clean_text(col) if isinstance(col, str) else col,
              inplace=True)

    # Clean all text cells (applymap is OK since text cleaning is cell-based)
    df = df.applymap(clean_text)

    # Remove duplicates & reset index
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Save final CSV
    df.to_csv(output_csv_path, index=False)

    print(f"Clean CSV saved to: {output_csv_path}")

excel_to_clean_csv("testdata.xlsx", "cleaned_testdata.csv")