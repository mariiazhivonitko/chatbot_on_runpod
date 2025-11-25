import requests
from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import AsyncConfig
from deepeval import evaluate


def call_chatbot(prompt):
    API_URL = "https://mbl0h54m0zdvum-8501.proxy.runpod.net/chat"
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


# Pull from Confident AI
dataset = EvaluationDataset()
dataset.pull(alias="CyTHIA-testdata")


# Run tests
# Create test cases from goldens
results = []
test_cases = []


for golden in dataset.goldens:
    response = call_chatbot(golden.input)
    test_case = LLMTestCase(input=golden.input, actual_output=response, expected_output=golden.expected_output, context=golden.context)
    test_cases.append(test_case)

#evaluate(test_cases, metrics, async_config=AsyncConfig(max_concurrent=1))
evaluate(test_cases, metric_collection="CyThIA", async_config=AsyncConfig(max_concurrent=1))


"""   # Evaluate each metric and store the score
    metric_scores = {}
    

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
#evaluate(test_cases, metrics) """