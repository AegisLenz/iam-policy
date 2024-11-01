import os
import json
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper

# JSON 파일 로드 함수
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        return None

# 여러 정책 병합 함수
def merge_policies(policies):
    merged_policy = {
        "Version": "2012-10-17",
        "Statement": []
    }
    action_resource_map = {}

    for policy in policies:
        for statement in policy.get("Statement", []):
            actions = statement.get("Action", [])
            resources = statement.get("Resource", [])
            actions = [actions] if isinstance(actions, str) else actions
            resources = [resources] if isinstance(resources, str) else resources

            for action in actions:
                if action not in action_resource_map:
                    action_resource_map[action] = set(resources)
                else:
                    action_resource_map[action].update(resources)

    for action, resources in action_resource_map.items():
        merged_policy["Statement"].append({
            "Action": action,
            "Resource": list(resources),
            "Effect": "Allow",
            "Sid": f"policy-{action}"
        })
    
    return merged_policy



def main():
    file_path = "/home/yjeongc/Downloads/iam-policy/src/ec2_sample_log.json"

    logs = load_json(file_path)
    if not isinstance(logs, list):
        print("Error: The log file does not contain a valid list of log entries.")
        return

    all_policies = []

    for log_entry in logs:
        if not isinstance(log_entry, dict):
            print("Error: Log entry is not a valid dictionary.")
            continue

        event_source = log_entry.get("eventSource")
        event_name = log_entry.get("eventName")
        user_identity = log_entry.get('userIdentity', {})
        user_name = log_entry.get('requestParameters', {}).get('userName')

        if event_source == 's3.amazonaws.com':
            specific_policy_path = os.path.join("/home/yjeongc/Downloads/iam-policy/AWSDatabase/S3", f'{event_name}.json')
            policy_data = load_json(specific_policy_path)
            if policy_data is not None:
                policy = s3_policy_mapper(log_entry, policy_data)
                if policy:
                    all_policies.append(policy)
        
        elif event_source == 'ec2.amazonaws.com':
            specific_policy_path = os.path.join("/home/yjeongc/Downloads/iam-policy/AWSDatabase/EC2", f'{event_name}.json')
            policy_data = load_json(specific_policy_path)
            if policy_data is not None:
                policy = ec2_policy_mapper(log_entry, policy_data)
                if policy:
                    all_policies.append(policy)
                    
        #elif event_source == 'iam.amazonaws.com':
            #추가해야 할 부분

        else :
            print(f"Unsupported event source: {event_source}")

    if not all_policies:
        print("No valid policies were generated.")
        return

    final_policy = merge_policies(all_policies)
    print(json.dumps(final_policy, indent=4))

if __name__ == "__main__":
    main()
