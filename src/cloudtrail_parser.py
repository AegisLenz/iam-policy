import json
import os
from collections import defaultdict

# CloudTrail 로그 파일을 열고 JSON 데이터를 로드하고, 필요한 정보를 추출하여 반환하는 함수
def load_and_extract_cloudtrail_logs(cloudtrail_log_filepath):
    try:
        with open(cloudtrail_log_filepath, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {cloudtrail_log_filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {cloudtrail_log_filepath}")
        return []

    context_data = defaultdict(dict)
    extracted_data_list = []

    for log_entry in logs:
        # 로그 항목에서 필요한 정보 추출
        event_name = log_entry.get('eventName')
        event_source = log_entry.get('eventSource')
        user_identity = log_entry.get('userIdentity', {})
        if isinstance(user_identity, str):
            user_identity = {}
        request_parameters = log_entry.get('requestParameters', {})
        response_elements = log_entry.get('responseElements', {})
        resources = log_entry.get('resources', [])

        # context_data에 필요한 데이터 저장 (예: accessKeyId 등)
        if response_elements:
            for key, value in response_elements.items():
                context_data[event_name][key] = value

        # 필요한 리소스 정보가 없으면 context_data에서 추적
        if not resources:
            resources = context_data.get(event_name, {}).get('resources', [])

        # 추출한 데이터를 리스트에 추가
        extracted_data_list.append({
            "eventName": event_name,
            "eventSource": event_source,
            "userIdentity": user_identity,
            "resources": resources,
            "requestParameters": request_parameters
        })

    return extracted_data_list
