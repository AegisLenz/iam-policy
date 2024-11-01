import os
import json
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper


# Step 1: JSON 파일 로드 함수
# JSON 파일을 로드하고, CloudTrail 로그 혹은 정책 템플릿으로 반환하는 함수
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 로그 파일 또는 정책 파일 반환
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None

# Step 5: 여러 정책 병합 함수
def merge_policies(policies):
    merged_policy = {
        "Version": "2012-10-17",
        "Statement": []
    }
    action_resource_map = {}

    for policy in policies:
        for statement in policy["Statement"]:
            action_tuple = tuple(statement["Action"])
            resource = statement["Resource"][0]

            if action_tuple in action_resource_map:
                action_resource_map[action_tuple].append(resource)
            else:
                action_resource_map[action_tuple] = [resource]

    for actions, resources in action_resource_map.items():
        merged_policy["Statement"].append({
            "Action": list(actions),
            "Resource": resources,
            "Effect": "Allow",
            "Sid": f"policy-{resources[0]}"
        })

    return merged_policy


def main():
    file_path = "/home/yjeongc/Downloads/iam-policy/src/ec2_sample_log.json"
    #file_path = "/home/yjeongc/Downloads/iam-policy/src/s3_sample_log.json"
    logs = load_json(file_path)
    if not isinstance(logs, list):
        print("Error: The log file does not contain a valid list of log entries.")
        return

    policy_folder_s3 = "/home/yjeongc/Downloads/iam-policy/AWSDatabase/S3"
    policy_folder_ec2 = "/home/yjeongc/Downloads/iam-policy/AWSDatabase/EC2"
    
    all_policies = []
    
    # 각 로그 항목에 대해 정책 파일을 로드하여 policy_data에 추가
    for log_entry in logs:
        if not isinstance(log_entry, dict):
            print("Error: Log entry is not a valid dictionary.")
            continue

        event_source = log_entry.get("eventSource")

        if event_source and event_source.startswith('s3'):
            event_name = log_entry.get("eventName")
            specific_policy_path = os.path.join(policy_folder_s3, f'{event_name}.json')
            policy_data = load_json(specific_policy_path)
            if policy_data is not None:
                policy = s3_policy_mapper(log_entry, policy_data)
                if policy:
                    all_policies.append(policy)
        
        elif event_source and event_source.startswith('ec2'):
            event_name = log_entry.get("eventName")
            specific_policy_path = os.path.join(policy_folder_ec2, f'{event_name}.json')
            policy_data = load_json(specific_policy_path)
            if policy_data is not None:
                policy = ec2_policy_mapper(log_entry, policy_data)
                if policy:
                    all_policies.append(policy)
        else:
            print(f"Unsupported event source: {event_source}")

    final_policy = merge_policies(all_policies)
    print(json.dumps(final_policy, indent=4))


if __name__ == "__main__":
    main()