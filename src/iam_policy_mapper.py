import os
import json

# Step 1: 리소스 추출 (IAM 또는 기타 서비스에 따른 리소스 설정)
def extract_resource_from_log(log):
    return log.get("eventSource", "unknown").split(".")[0]

# Step 2: 리소스를 매핑하는 함수 (IAM)
# 로그의 정보를 정책 템플릿에 매핑하여 최소 권한 정책을 생성
def iam_map_resource(log):
    account_id = log.get("userIdentity", {}).get("accountId")
    user_name = log.get("userIdentity", {}).get("userName")
    
    resource_arn = f"arn:aws:iam::{account_id}:user/{user_name}"
    resource_list = [resource_arn]
    
    return resource_list

# Step 3: 최소 권한 정책 생성 함수
def generate_least_privilege_policy(resource, resource_list, event_name):
    least_privilege_policies = []
    action = f"{resource}:{event_name}"
    
    for resource in resource_list:
        policy_template = {
            "Action": [action],
            "Resource": [resource],
            "Effect": "Allow",
            "Sid": f"policy-{resource}"
        }
        least_privilege_policies.append(policy_template)
    
    return least_privilege_policies

# Step 4: 최소 권한 정책 생성 함수
def iam_policy_mapper(log):
    # 리소스 추출
    resource = extract_resource_from_log(log)
    
    # 로그에서 필요한 필드 추출 및 리소스 매핑
    resource_list = iam_map_resource(log)
    
    # 이벤트 이름 추출
    event_name = log.get("eventName", "UnknownEvent")
    
    # 최소 권한 정책 생성
    least_privilege_policies = generate_least_privilege_policy(resource, resource_list, event_name)
    
    # 최종 정책 구성 및 반환
    final_policy = {
        "Version": "2012-10-17",
        "Statement": least_privilege_policies
    }
    
    return final_policy