from extract_policy_by_cloudTrail import extract_policy_by_cloudTrail
from comparePolicy import clustered_compare_policy
from common_utils import load_json
import json

def main():
    log_path = "./sample_data/logs.json"
    #r"src\sample_data\iam__backdoor_assume_O_1.json"
    userPolicy_path = "./sample_data/userPolicy.json"
    #userPolicy_path = r"src\sample_data\userPolicy.json"
    userPolicy = load_json(userPolicy_path)

    print("기존의 Policy: ")
    print(json.dumps(userPolicy, indent=4))

    clustered_policy_by_cloudtrail = extract_policy_by_cloudTrail(log_path)
    print("최소권한 Policy: ")
    print(json.dumps(clustered_policy_by_cloudtrail, indent=4))

    should_remove_actions = clustered_compare_policy(userPolicy, clustered_policy_by_cloudtrail)
    converted_actions = {k: [list(v) for v in val] for k, val in should_remove_actions.items()}
    print(f"삭제해야 할 action: {json.dumps(converted_actions, indent=4, ensure_ascii=False)}")

if __name__ == "__main__":
    main()