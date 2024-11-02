# main.py
import os
import json
from common_utils import load_json, merge_policies
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper
from iam_policy_mapper import iam_policy_mapper

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
        elif event_source == 'iam.amazonaws.com':
            policy = iam_policy_mapper(log_entry)
            if policy:
                all_policies.append(policy)
        else:
            action = f"{event_source.split('.')[0]}:{event_name}"
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": f"policy-{action}",
                        "Action": action,
                        "Resource": "*",
                        "Effect": "Allow",
                    }
                ]
            }
            all_policies.append(policy)

    if not all_policies:
        print("No valid policies were generated.")
        return

    final_policy = merge_policies(all_policies)
    print(json.dumps(final_policy, indent=4))

if __name__ == "__main__":
    main()
