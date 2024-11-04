# main.py
import os
import json
from common_utils import load_json, merge_policies, map_etc
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper
from iam_policy_mapper import iam_policy_mapper

def extract_policy_by_cloudTrail(file_path):
    logs = load_json(file_path).get("Records",[])
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
            specific_policy_path = os.path.join("./../AWSDatabase/S3", f'{event_name.casefold()}.json')
            if os.path.exists(specific_policy_path):
                policy_data = load_json(specific_policy_path)
                policy = s3_policy_mapper(log_entry, policy_data)
            else:
                policy = map_etc(event_source, event_name)

            if policy:
                    all_policies.append(policy)

        elif event_source == 'ec2.amazonaws.com':
            specific_policy_path = os.path.join("./../AWSDatabase/EC2", f'{event_name.casefold()}.json')
            if os.path.exists(specific_policy_path):
                policy_data = load_json(specific_policy_path)
                policy = ec2_policy_mapper(log_entry, policy_data)
            else:
                policy = map_etc(event_source, event_name)

            if policy:
                    all_policies.append(policy)
                    
        elif event_source == 'iam.amazonaws.com':
            policy = iam_policy_mapper(log_entry)
            if policy:
                all_policies.append(policy)
        else:
            policy = map_etc(event_source, event_name)
            all_policies.append(policy)

    if not all_policies:
        print("No valid policies were generated.")
        return

    final_policy = merge_policies(all_policies)
    return final_policy

