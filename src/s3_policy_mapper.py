import os
import json

# Step 2: 리소스를 매핑하는 함수 (S3)
# 로그의 정보를 정책 템플릿에 매핑하여 최소 권한 정책을 생성
def s3_map_resource(policy_data, log):
    mapping = {
        "bucket_name": log.get("requestParameters", {}).get("bucketName"),
        "object_key": log.get("requestParameters", {}).get("key"),
        "key_prefix": log.get("requestParameters", {}).get("keyPrefix"),
    }
    
    resource_list = []
    resources = log.get('resources', [])
    # 리소스 필드에 ARN이 있는지 확인
    if resources:
        for resource in resources:
            if 'ARN' in resource:
                resource_list.append(resource['ARN'])
                return resource_list
    
    # 정책 데이터의 리소스를 순회하며 로그에서 추출한 값을 사용해 리소스를 매핑
    for statement in policy_data.get("policy", []):
        for i, resource in enumerate(statement.get("Resource", [])):
            for key, value in mapping.items():
                if value:
                    resource = resource.replace(f"{{{key}}}", value)
            resource_list.append(resource)

    # 지원되지 않는 이벤트에 대한 기본 리소스 설정
    if not resource_list:
        resource_list.append("*")
    
    return resource_list

# Step 3: 최소 권한 정책 생성 함수
def generate_least_privilege_policy(policy_data, resource_list):
    least_privilege_policies = []
    for statement in policy_data.get("policy", []):
        actions = statement.get("Action", [])
        for resource in resource_list:
            policy_template = {
                "Action": actions,
                "Resource": [resource],
                "Effect": "Allow",
                "Sid": f"policy-{resource}"
            }
            least_privilege_policies.append(policy_template)
    return least_privilege_policies

# Step 4: S3 정책 템플릿 로드 및 최소 권한 정책 생성 함수
def s3_policy_mapper(log, policy_data):
    # 로그에서 필요한 필드 추출 및 리소스 매핑
    resource_list = s3_map_resource(policy_data, log)
    
    # 최소 권한 정책 생성
    least_privilege_policies = generate_least_privilege_policy(policy_data, resource_list)
    
    # 최종 정책 구성 및 저장
    final_policy = {
        "Version": "2012-10-17",
        "Statement": least_privilege_policies
    }
    
    return final_policy