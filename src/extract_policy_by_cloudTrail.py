# main.py
import os
import json
from common_utils import load_json, merge_policies, map_etc
from s3_policy_mapper import s3_policy_mapper
from ec2_policy_mapper import ec2_policy_mapper
from iam_policy_mapper import iam_policy_mapper


def clustering_by_username(file_path):
    logs = load_json(file_path).get("Records",[])
    cluster = {}
    for log in logs:
        userIdentity = log.get("userIdentity",{})
        if "userName" in userIdentity:
            userName = userIdentity["userName"]
        elif userIdentity.get("type") == "Root":
            userName = "root"
        else:
            userName = "AWS"

        if userName not in cluster:
            cluster[userName] = [] 
        cluster[userName].append(log)
    return cluster


def making_policy(log_entry):
    event_source = log_entry.get("eventSource")
    event_name = log_entry.get("eventName")

    if event_source == 's3.amazonaws.com':
        specific_policy_path = os.path.join("AWSDatabase\S3", f'{event_name.casefold()}.json')
        if os.path.exists(specific_policy_path):
            policy_data = load_json(specific_policy_path)
            policy = s3_policy_mapper(log_entry, policy_data)
        else:
            policy = map_etc(event_source, event_name)

    elif event_source == 'ec2.amazonaws.com':
        specific_policy_path = os.path.join("AWSDatabase\EC2", f'{event_name.casefold()}.json')
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
    logs = load_json(file_path).get("Records", [])
    if not isinstance(logs, list):
        print("Error: The log file does not contain a valid list of log entries.")
        return
    
    cluster = clustering_by_username(file_path) # 사용자별 클러스터링 추가
    policies_by_user = {} # 사용자별로 정책을 저장하기 위한 딕셔너리 생성

    for userName, user_logs in cluster.items():
        service_policies = {} # 사용자별 서비스 정책 생성 추가

        for log_entry in user_logs:
            if not isinstance(log_entry, dict):
                print("Error: Log entry is not a valid dictionary.")
                continue

            event_source = log_entry.get("eventSource")
            if event_source not in service_policies: # 서비스별로 정책을 분리하여 저장
                service_policies[event_source] = []

            policy = making_policy(log_entry) # 개별 로그로부터 정책 생성
            if policy:
                service_policies[event_source].append(policy)

        user_policies = []
        for service, policies in service_policies.items():
            merged_policy = merge_policies(policies) # 서비스별 리소스별로 액션을 묶어서 병합
            user_policies.append({
                "Service": service, # 서비스별로 정책 생성 추가
                "Policy": merged_policy
            })

        policies_by_user[userName] = user_policies # 사용자별로 정책 클러스터링 추가
    return policies_by_user



