# main.py
import os
import json
from common_utils import load_json, merge_policies, map_etc
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper
from iam_policy_mapper import iam_policy_mapper


def clustering_by_username(file_path):
    logs = load_json(file_path).get("Records", [])
    cluster = {}
    for log in logs:
        userIdentity = log.get("userIdentity", {})
        userName = userIdentity.get("userName")
        if userName not in cluster:
            cluster[userName] = []  
        cluster[userName].append(log)

    return cluster   

def making_policy(log_entry):
    event_source = log_entry.get("eventSource")
    event_name = log_entry.get("eventName")

    if event_source == 's3.amazonaws.com':
        specific_policy_path = os.path.join("./../AWSDatabase/S3", f'{event_name.casefold()}.json')
        if os.path.exists(specific_policy_path):
            policy_data = load_json(specific_policy_path)
            policy = s3_policy_mapper(log_entry, policy_data)
        else:
            policy = map_etc(event_source, event_name)

    elif event_source == 'ec2.amazonaws.com':
        specific_policy_path = os.path.join("./../AWSDatabase/EC2", f'{event_name.casefold()}.json')
        if os.path.exists(specific_policy_path):
            policy_data = load_json(specific_policy_path)
            policy = ec2_policy_mapper(log_entry, policy_data)
        else:
            policy = map_etc(event_source, event_name)
                    
    elif event_source == 'iam.amazonaws.com':
        policy = iam_policy_mapper(log_entry)

    else:
        policy = map_etc(event_source, event_name)

    return policy

def extract_policy_by_cloudTrail(file_path):
    logs = load_json(file_path).get("Records",[])
    if not isinstance(logs, list):
        print("Error: The log file does not contain a valid list of log entries.")
        return
    
    normal_log = []
    all_policies = []
    clustered_policy={}
    cluster = clustering_by_username(file_path)

    for userName in cluster.keys():
        #attack에서만 단독적으로 사용된 권한 제외
        for log_entry in cluster[userName]:
            if not isinstance(log_entry, dict):
                print("Error: Log entry is not a valid dictionary.")
                continue

            isAttack = log_entry.get("mitreAttackTactic")
            policy = making_policy(log_entry)
            if policy:
                if isAttack is None:
                    normal_log.append(log_entry)

        #Attack고려한 최소권한 추출
        for log_entry in normal_log:
            if not isinstance(log_entry, dict):
                print("Error: Log entry is not a valid dictionary.")
                continue

            policy = making_policy(log_entry)
            all_policies.append(policy)

        if not all_policies:
            print("No valid policies were generated.")
            return

        final_policy = merge_policies(all_policies)
        if userName not in clustered_policy:
            clustered_policy[userName] = []
        clustered_policy[userName].append(final_policy)
    return clustered_policy






