import json
import pandas as pd
import textstat

# Load deepeval-cache.json
with open(".deepeval-cache.json", "r", encoding="utf-8") as f:
    cache = json.load(f)

# Extract actual outputs
actual_outputs = []
for key_str in cache.get("test_cases_lookup_map", {}):
    test_case_data = json.loads(key_str)
    actual_output = test_case_data.get("actual_output")
    actual_outputs.append(actual_output)

# Compute readability metrics
results = []

for i, text in enumerate(actual_outputs, 1):
    if not text or not text.strip():
        metrics = {
            "Flesch-Kincaid": None,
            "Flesch": None,
            "Gunning-Fog": None,
            "ARI": None,
            "SMOG": None
        }
    else:
        try:
            metrics = {
                "Flesch-Kincaid": textstat.flesch_kincaid_grade(text),
                "Flesch": textstat.flesch_reading_ease(text),
                "Gunning-Fog": textstat.gunning_fog(text),
                "ARI": textstat.automated_readability_index(text),
                "SMOG": textstat.smog_index(text)
            }
        except Exception as e:
            metrics = {
                "Flesch-Kincaid": None,
                "Flesch": None,
                "Gunning-Fog": None,
                "ARI": None,
                "SMOG": None
            }
            print(f"Error for output {i}: {e}")

    results.append({
        "output_index": i,
        "actual_output": text,
        **metrics
    })

# Convert to DataFrame
df_readability = pd.DataFrame(results)

# Calculate averages (skip None values)
average_metrics = df_readability[["Flesch-Kincaid", "Flesch", "Gunning-Fog", "ARI", "SMOG"]].mean(skipna=True)
df_averages = pd.DataFrame([average_metrics])

# Save detailed results and averages to Excel
with pd.ExcelWriter("actual_outputs_readability.xlsx") as writer:
    df_readability.to_excel(writer, sheet_name="Readability Results", index=False)
    df_averages.to_excel(writer, sheet_name="Readability Averages", index=False)

print("Readability metrics and averages saved to actual_outputs_readability.xlsx")
