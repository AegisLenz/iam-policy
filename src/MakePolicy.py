#MakePolicy.py
import os
from parsingData import parsingData  # CloudTrail 로그에서 데이터를 추출하는 모듈
from ActionMapping import map_event_to_permissions  # 이벤트와 액션을 매핑하는 모듈
import json
import copy
from collections import OrderedDict  # 키 순서를 유지하기 위해 사용

# 정책 템플릿 기본 구조
policies = {
    "Statement": []
}

# 각 정책에 사용될 기본 템플릿
policy_template = {
    "Action": [],
    "Resource": [],
    "Effect": "Allow",
    "Sid": ""
}

# 정책을 생성하는 함수
def make_policy_from_event(event_name, actions, resources):
    # 정책을 생성하는 로직
    policy = copy.deepcopy(policy_template)
    policy["Action"] = actions
    
    # 리소스가 있다면 리소스를 추가, 없으면 "*"
    if resources and len(resources) > 0:
        policy["Resource"] = resources
    else:
        policy["Resource"] = ["*"]  # 리소스가 없을 때 기본값으로 "*"를 설정

    policy["Sid"] = f"policy-{event_name}"  # Sid는 event_name을 기반으로 설정

    # 생성된 정책을 전역 policies에 추가
    policies["Statement"].append(policy)

# CloudTrail 로그와 정책 파일을 사용해 정책을 생성하는 함수
def process_cloudtrail_and_create_policies(cloudtrail_file, policy_folder):
    # CloudTrail 로그에서 데이터를 추출
    cloudtrail_data = parsingData(cloudtrail_file)
    
    # 중복을 방지하기 위해 eventName을 저장할 set 사용
    unique_event_names = set()

    # 각 eventName에 맞는 액션을 매핑
    event_permissions = map_event_to_permissions(cloudtrail_file, policy_folder)

    # CloudTrail 로그에 있는 각 이벤트에 대해 정책을 생성
    for event in cloudtrail_data:
        event_name = event.get("eventName")
        resources = event.get("resources", [])

        # 중복된 eventName을 처리하지 않도록 set에 없는 경우에만 추가
        if event_name not in unique_event_names:
            unique_event_names.add(event_name)
            actions = event_permissions.get(event_name, [])
            
            if actions:  # 액션이 존재하면 정책 생성
                make_policy_from_event(event_name, actions, resources)

# 정책을 텍스트 파일로 저장하는 함수
def save_policies_to_txt(file_name):
    # 텍스트 파일로 정책을 저장
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(ordered_policies, file, indent=4)
        print(f"Policies have been saved to {file_name}")

# 정책이 들어있는 폴더 경로 설정 및 CloudTrail 로그 파일 경로 설정
policy_folder = "/home/yjeongc/Downloads/Policy"
cloudtrail_log_filepath = "/home/yjeongc/Downloads/iam__backdoor_assume_role_policy_O1.json"

# CloudTrail 로그에 맞춰 정책 생성
process_cloudtrail_and_create_policies(cloudtrail_log_filepath, policy_folder)

# 생성된 정책을 출력 (순서대로 출력하기 위해 OrderedDict 사용)
ordered_policies = OrderedDict([
    ("Statement", [])
])

for statement in policies["Statement"]:
    ordered_policy = OrderedDict([
        ("Action", statement["Action"]),
        ("Resource", statement["Resource"]),
        ("Effect", statement["Effect"]),
        ("Sid", statement["Sid"])
    ])
    ordered_policies["Statement"].append(ordered_policy)

# 생성된 정책을 보기 좋게 출력
print(json.dumps(ordered_policies, indent=4))

# 정책을 json 파일로 저장
output_json_file = "generated_policies02.json"
save_policies_to_txt(output_json_file)

