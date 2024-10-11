import os
from policy_handler import load_policy_template, generate_resource

# 로그 데이터와 정책 파일을 이용해 리소스와 액션을 맵핑하는 함수
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

        # 리소스별로 액션을 맵핑하여 정책 생성
        for resource in resources:
            if resource in resource_policies:
                for action in actions:
                    if action not in resource_policies[resource]["Action"]:
                        resource_policies[resource]["Action"].append(action)
            else:
                resource_policies[resource] = {"Action": actions}

    return resource_policies


# 리소스와 액션 리스트를 기반으로 정책을 생성하는 함수
def make_policy_from_resource(resource, actions):
    policy_template = {
        "Action": actions,
        "Resource": [resource],
        "Effect": "Allow",
        "Sid": f"policy-{resource}"
    }
    return policy_template
