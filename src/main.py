from extract_policy_by_cloudTrail import extract_policy_by_cloudTrail
from comparePolicy import comparePolicy
from common_utils import load_json
import json

def main():
    log_path = "./sample_data/attacklog.json"
    userPolicy_path = "./sample_data/userPolicy.json"
    userPolicy = load_json(userPolicy_path)

    print("기존의 Policy: ")
    print(json.dumps(userPolicy, indent=4))

    policy_by_cloudTrail = extract_policy_by_cloudTrail(log_path)
    print("최소권한 Policy: ")
    print(json.dumps(policy_by_cloudTrail, indent=4))

    should_remove_action = comparePolicy(userPolicy, policy_by_cloudTrail)
    print(f"삭제해야 할 action: {should_remove_action}")

if __name__ == "__main__":
    main()