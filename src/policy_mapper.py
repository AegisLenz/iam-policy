#policy_mapper.py
import os
from policy_handler import load_policy_template, generate_resource

# 로그 데이터와 정책 파일을 이용해 리소스와 액션을 맥핏하는 함수
def map_event_to_permissions(logs, policy_folder):
    resource_policies = {}
    policy_files = {f.replace('.json', ''): os.path.join(policy_folder, f) for f in os.listdir(policy_folder) if f.endswith('.json')}

    for log_entry in logs:
        event_name = log_entry.get("eventName")
        event_source = log_entry.get("eventSource")
        policy_template = load_policy_template(event_name, policy_folder, event_source)
        resources = generate_resource(log_entry, policy_template, logs)

        # 정책 파일이 있는 경우 해당 정책 템플릿에서 액션을 가져옴
        if event_name in policy_files and policy_template:
            actions = policy_template.get("policy", {}).get("Action", [])
        else:
            # 정책 파일이 없으면 기본 Action 생성
            actions = [f"{event_source.split('.')[0]}:{event_name}"] if event_source else []

        # IAM 관련 이벤트 처리 (이벤트 소스가 'iam.amazonaws.com'인 경우)
        if event_source == 'iam.amazonaws.com':
            iam_action = f"iam:{event_name}"
            if iam_action not in actions:
                actions.append(iam_action)

        # 리소스별로 액션을 맥핏해서 정책 생성
        for resource in resources:
            if resource in resource_policies:
                resource_policies[resource]["Action"].extend([action for action in actions if action not in resource_policies[resource]["Action"]])
            else:
                resource_policies[resource] = {"Action": actions.copy()}

    # 모든 IAM 관련 이벤트의 액션을 누적해서 처리
    all_iam_actions = []
    for log_entry in logs:
        event_name = log_entry.get("eventName")
        event_source = log_entry.get("eventSource")
        if event_source == 'iam.amazonaws.com':
            iam_action = f"iam:{event_name}"
            if iam_action not in all_iam_actions:
                all_iam_actions.append(iam_action)

    # IAM 관련 리소스에 누적된 모든 액션 추가
    for resource in resource_policies:
        if resource.startswith("arn:aws:iam"):
            resource_policies[resource]["Action"].extend([action for action in all_iam_actions if action not in resource_policies[resource]["Action"]])

    # 정책 생성 중 리소스별 Action 중복 제거
    for resource in resource_policies:
        resource_policies[resource]["Action"] = list(set(resource_policies[resource]["Action"]))

    return resource_policies


# 리소스와 액션 리스트를 기반으로 정책을 생성하는 함수
def make_policy_from_resource(resource, actions):
    policy_template = {
        "Action": list(set(actions)),
        "Resource": [resource],
        "Effect": "Allow",
        "Sid": f"policy-{resource}"
    }
    return policy_template