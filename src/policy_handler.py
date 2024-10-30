from ec2_policy_mapper import ec2_policy_mapper, load_json
import os
import json

def save_mapped_policy(policy_data, output_path):
    try:
        with open(output_path, 'w') as file:
            json.dump(policy_data, file, indent=4)
        print(f"Mapped policy saved to {output_path}")
    except IOError:
        print(f"Error: Could not write to file {output_path}")

def format_policy(merged_policy):
    policies = {"policy": []}
    policy_data = merged_policy.get("policy",{})
    for action in policy_data.keys():
        effect = policy_data[action].get("Effect")
        resource = policy_data[action].get("Resource")
        policies["policy"].append({
            "Sid": f"policy-{resource}",
            "Action": action,
            "Effect": effect,
            "Resource": resource
            
        })

    return policies

def merge_policies(policy_data_list):
    # 중복되지 않게 정책을 병합하는 함수
    merged_policy = {"policy": {}}
    unique_action = set()

    for policy_data in policy_data_list:
        for statement in policy_data.get("policy", []):
            # Resource가 리스트가 아닌 경우 리스트로 변환
            resources = statement.get("Resource", [])
            if not isinstance(resources, list):
                resources = [resources]

            actions = statement.get("Action")
            effect = statement.get("Effect")

            # action별로 Resource 목록을 병합하여 저장
            for action in actions:
                if action not in unique_action:
                    merged_policy["policy"][action] = {
                        "Effect": effect,
                        "Resource": list(set(resources))  # 중복 제거 후 추가
                    }
                    unique_action.add(action)
                else:
                    # 이미 action이 있다면 기존 Resource 목록에 중복되지 않게 추가
                    existing_resources = set(merged_policy["policy"][action]["Resource"])
                    merged_policy["policy"][action]["Resource"] = list(existing_resources.union(resources))

    return format_policy(merged_policy)

def make_policy(log_path):
    logs = load_json(log_path)
    all_policies = []

    for log in logs:
        resource = log.get("eventSource").split(".")[0]
        if resource == "ec2":
            policy_buf = ec2_policy_mapper(log)

        else:
            #policy_buf = 유정햄 함수
            print(2)

        all_policies.append(policy_buf)
    policy = merge_policies(all_policies)
    return policy

path = "./ex.json"
policy = make_policy(path)
print(json.dumps(policy, indent= 4))