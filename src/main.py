#main.py
from cloudtrail_parser import load_and_extract_cloudtrail_logs
from policy_mapper import map_event_to_permissions, make_policy_from_resource
import json

# 정책 생성 및 저장을 위한 실행 코드
policy_folder = "정책_템플릿_폴더경로"
cloudtrail_log_filepath = "CloudTrail_Log_파일경로"
output_json_file = "sample_정책_저장경로"

# CloudTrail 로그를 분석하여 필요한 데이터를 추출
logs = load_and_extract_cloudtrail_logs(cloudtrail_log_filepath)

# 이벤트와 리소스를 매핑하여 정책 생성
resource_policies = map_event_to_permissions(logs, policy_folder)

# 최종 정책 생성 및 저장
policies = {"Statement": []}
for resource, policy_data in resource_policies.items():
    actions = policy_data["Action"]
    policy = make_policy_from_resource(resource, actions)
    policies["Statement"].append(policy)

with open(output_json_file, 'w', encoding='utf-8') as file:
    json.dump(policies, file, indent=4)
    print(f"Policies have been saved to {output_json_file}")