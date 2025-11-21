from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval import assert_test
import pandas as pd
import requests
import re

def clean_text(text):
    if not isinstance(text, str):
        return text
    
    # Normalize quotation marks and apostrophes
    text = text.replace("’", "'")  # apostrophe
    text = text.replace("“", '"').replace("”", '"')  # quotation marks

    # Replace non-breaking spaces with normal spaces
    text = text.replace("\xa0", " ")

    # Remove BOM and other invisible characters
    text = text.replace("\ufeff", "")

    # Remove other control characters
    text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)

    # Strip whitespace
    text = text.strip()

    return text

def call_chatbot(prompt):
    API_URL = "https://lnd23kmtrdj1oz-8501.proxy.runpod.net/chat"
    MODEL_NAME = "CyThIA-Mistral"

    try:
        response_data = requests.post(
            f"{API_URL}/{MODEL_NAME}",
            json={"message": prompt},
            timeout=120  # wait max 2 minutes
        )
        response_data.raise_for_status()
        response = response_data.json().get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        response = f"The chatbot service is temporarily unavailable."

    return response


#load dataset from xlsx
df=pd.read_excel("testdata.xlsx")

# Create Goldens
goldens=[]
for index, row in df.iterrows():
    goldens.append(Golden(input=clean_text(row['input']), expected_output=clean_text(row['expected_output'])))

# Create EvaluationDataset
dataset = EvaluationDataset(goldens=goldens)

#define evaluation metrics
correctness_metric = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct based on the expected output.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
)

relevance_metric = GEval(
    name="Relevance",
    criteria="Determine if the actual output is relevant to the input question.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
)

coherence_metric = GEval(
    name="Coherence",
    criteria="Determine if the actual output is logically coherent, consistent, and easy to follow.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
)

tonality_metric = GEval(
    name="Tonality (Professionalism)",
    criteria="Determine if the actual output is professional, polite, and appropriate for a business/security context.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
)
metrics = [correctness_metric, relevance_metric, coherence_metric, tonality_metric]

# Run tests
# Create test cases from goldens
results = []
test_cases = []

for golden in dataset.goldens:
    response = call_chatbot(golden.input)
    test_case = LLMTestCase(input=golden.input, actual_output=response, expected_output=golden.expected_output)
    test_cases.append(test_case)

    # Evaluate each metric and store the score
    metric_scores = {}
    for metric in metrics:
        score = metric.evaluate(test_case)
        metric_scores[metric.name] = score

    # Store results
    results.append({
        "input": golden.input,
        "actual_output": response,
        "expected_output": golden.expected_output,
        **metric_scores
    })

# -------------------- Compute average scores --------------------
average_scores = {metric.name: sum(r[metric.name] for r in results)/len(results) for metric in metrics}
print("Average metric scores:")
for metric_name, avg in average_scores.items():
    print(f"{metric_name}: {avg:.3f}")

# -------------------- Save detailed results and averages to Excel --------------------
results_df = pd.DataFrame(results)
averages_df = pd.DataFrame([average_scores])

with pd.ExcelWriter("chatbot_evaluation_results.xlsx") as writer:
    results_df.to_excel(writer, sheet_name="Results", index=False)
    averages_df.to_excel(writer, sheet_name="Averages", index=False)

print("\nDetailed results and average metrics saved to chatbot_evaluation_results.xlsx")