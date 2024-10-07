#eventname과 Action을 맵핑하는 코드
import json
import os

# CloudTrail 로그에서 중복되지 않는 eventName을 추출하는 함수
def extract_unique_event_names(cloudtrail_log_filepath):
    try:
        with open(cloudtrail_log_filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {cloudtrail_log_filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {cloudtrail_log_filepath}")
        return []

    event_names = set()

    # 로그 데이터가 리스트일 경우 처리
    if isinstance(log_data, list):
        for record in log_data:
            event_name = record.get("eventName")
            if event_name:
                event_names.add(event_name)
    else:
        print("Unexpected JSON format: expected a list of records.")

    return list(event_names)

# 정책 파일에서 Action 필드의 최소 권한을 추출하는 함수
def get_min_permissions_from_policy(policy_file_path):
    try:
        with open(policy_file_path, 'r', encoding='utf-8') as policy_file:
            policy_data = json.load(policy_file)
        actions = policy_data.get("policy", {}).get("Action", [])
        return actions if actions else None
    except FileNotFoundError:
        print(f"Policy file not found: {policy_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from policy file: {policy_file_path}")
        return None

# eventSource와 eventName을 조합하여 기본 Action을 생성하는 함수
def generate_action_from_event_source(event_source, event_name):
    if event_source:
        service_prefix = event_source.split('.')[0]  # eventSource의 앞부분 추출
        return f"{service_prefix}:{event_name}"
    return None

# eventName과 정책 파일을 매핑하여 최소 권한을 반환하는 함수
def get_permissions_for_event(event_name, policy_files, policy_folder, event_source=None):
    if event_name in policy_files:
        policy_file_path = os.path.join(policy_folder, f"{event_name}.json")
        min_permissions = get_min_permissions_from_policy(policy_file_path)
        return min_permissions if min_permissions else f"No permissions found for {event_name}."
    else:
        # 정책 파일이 없을 경우 eventSource를 사용하여 Action 생성
        if event_source:
            generated_action = generate_action_from_event_source(event_source, event_name)
            return [generated_action] if generated_action else f"Could not generate Action for {event_name}."
        return f"Policy file for {event_name} does not exist and could not generate Action."

# 정책 폴더 내의 모든 정책 파일 리스트를 반환하는 함수
def get_policy_files(policy_folder):
    policy_files = []
    for filename in os.listdir(policy_folder):
        if filename.endswith(".json"):
            policy_files.append(filename.replace('.json', ''))
    return policy_files

# CloudTrail 이벤트와 액션을 매핑하는 함수
def map_event_to_permissions(cloudtrail_log_filepath, policy_folder):
    event_names = extract_unique_event_names(cloudtrail_log_filepath)
    policy_files = get_policy_files(policy_folder)

    event_permission_mapping = {}
    for event_name in event_names:
        # 로그 파일에서 eventSource를 얻어옴
        event_source = extract_event_source_from_log(cloudtrail_log_filepath, event_name)
        permissions = get_permissions_for_event(event_name, policy_files, policy_folder, event_source)
        event_permission_mapping[event_name] = permissions
    
    return event_permission_mapping

# CloudTrail 로그에서 특정 eventName에 대한 eventSource를 추출하는 함수
def extract_event_source_from_log(cloudtrail_log_filepath, target_event_name):
    try:
        with open(cloudtrail_log_filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {cloudtrail_log_filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {cloudtrail_log_filepath}")
        return None

    # 로그 데이터가 리스트일 경우 처리
    if isinstance(log_data, list):
        for record in log_data:
            event_name = record.get("eventName")
            event_source = record.get("eventSource")
            if event_name == target_event_name and event_source:
                return event_source
    return None



