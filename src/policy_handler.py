#policy_handler.py
#policy_handler.py
import os
import json

# 특정 이벤트 이름에 해당하는 정책 템플릿 파일을 로드하는 함수
# event_source가 's3.amazonaws.com'인 경우에만 로드함
def load_policy_template(event_name, policy_folder_path, event_source):

    if event_source != 's3.amazonaws.com':
        return None

    policy_file_path = os.path.join(policy_folder_path, f'{event_name}.json')
    if os.path.exists(policy_file_path):
        try:
            with open(policy_file_path, 'r', encoding='utf-8') as file:
                policy_data = json.load(file)
                return policy_data
        except json.JSONDecodeError:
            print(f"Error decoding JSON from policy file: {policy_file_path}")
    else:
        print(f"Policy file not found: {policy_file_path}")
    return None


# 로그 항목과 정책 템플릿을 사용해 필요한 리소스를 생성하는 함수
def generate_resource(log_entry, policy_template, context_data):

    resource_list = []
    resources = log_entry.get('resources', [])

    # 1. resources 필드에 ARN이 있는지 확인
    if resources:
        for resource in resources:
            if 'ARN' in resource:
                resource_list.append(resource['ARN'])
                return resource_list

    # 정책 템플릿에 리소스 필드가 있는 경우 자리 표시자를 채워 리소스 생성
    if policy_template and "Resource" in policy_template["policy"]:
        for resource in policy_template["policy"]["Resource"]:
            if '{bucket_name}' in resource:
                bucket_name = log_entry.get('requestParameters', {}).get('bucketName')
                if not bucket_name:
                    bucket_name = context_data.get(log_entry.get('eventName'), {}).get('bucketName')
                if bucket_name:
                    resource = resource.replace('{bucket_name}', bucket_name)
            if '{object_key}' in resource:
                object_key = log_entry.get('requestParameters', {}).get('key')
                if not object_key:
                    object_key = context_data.get(log_entry.get('eventName'), {}).get('key')
                if object_key:
                    resource = resource.replace('{object_key}', object_key)
            if '{key_prefix}' in resource:
                key_prefix = log_entry.get('requestParameters', {}).get('keyPrefix')
                if not key_prefix:
                    key_prefix = context_data.get(log_entry.get('eventName'), {}).get('keyPrefix')
                if key_prefix:
                    resource = resource.replace('{key_prefix}', key_prefix)
            resource_list.append(resource)

    # IAM 관련 이벤트 처리 (event_source가 'iam.amazonaws.com'인 경우)
    if log_entry.get('eventSource') == 'iam.amazonaws.com':
        user_identity = log_entry.get('userIdentity', {})
        user_name = log_entry.get('requestParameters', {}).get('userName')
        if user_name:
            resource_arn = f"arn:aws:iam::{user_identity.get('accountId', log_entry.get('recipientAccountId', 'unknown'))}:user/{user_name}"
            if resource_arn not in resource_list:
                resource_list.append(resource_arn)

    # 그 외의 이벤트 처리
    if not resource_list:
        general_resource = f"*"
        if general_resource not in resource_list:
            resource_list.append(general_resource)

    return resource_list