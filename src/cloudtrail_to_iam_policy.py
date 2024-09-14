from parsingData import parsingData
import json
import copy

file_path = "D:\\bob\\AegisLenz\\dataset\\iam_privesc_by_rollback_O\\iam_privesec_by_rollback_O (1).json"

# 정책 템플릿
policies = {
    "Statement": []
}

policy_template = {
    "Sid": "",
    "Effect": "Allow",
    "Action": [],
    "Resource": []
}

def makeField(file_path):
    extracted_data_list = parsingData(file_path)
    
    # 리소스별로 정책을 추적하기 위한 딕셔너리
    resource_policies = {}

    for data in extracted_data_list:
        eventName = data.get("eventName")
        eventSource = data.get('eventSource')
        resources = data.get("resources")
        errorCode = data.get("errorCode")

        if errorCode:
            continue

        # eventSource에서 서비스 이름 추출
        tmp = eventSource.split(".")
        resource_type = tmp[0]

        # 리소스가 있는 경우
        if resources:
            for resource in resources:
                arn = resource.get("ARN")
                if arn:
                    # 이미 존재하는 리소스에 대한 정책이 있다면, 기존 정책에 액션 추가
                    if arn in resource_policies:
                        if f"{resource_type}:{eventName}" not in resource_policies[arn]["Action"]:
                            resource_policies[arn]["Action"].append(f"{resource_type}:{eventName}")
                    else:
                        # 새로운 리소스에 대한 정책 생성
                        new_policy = copy.deepcopy(policy_template)
                        new_policy["Action"].append(f"{resource_type}:{eventName}")
                        new_policy["Resource"].append(arn)
                        new_policy["Sid"] = f"policy-{len(resource_policies) + 1}"  # 고유 Sid 생성
                        resource_policies[arn] = new_policy
        else:
            # 리소스가 없는 경우, 글로벌 액션 처리 (Resource: "*")
            if "*" in resource_policies:
                # 이미 존재하는 글로벌 정책에 액션이 있는지 확인
                if f"{resource_type}:{eventName}" not in resource_policies["*"]["Action"]:
                    resource_policies["*"]["Action"].append(f"{resource_type}:{eventName}")
            else:
                # 새로운 글로벌 정책 생성
                new_policy = copy.deepcopy(policy_template)
                new_policy["Action"].append(f"{resource_type}:{eventName}")
                new_policy["Resource"].append("*")  # 리소스가 없는 경우, 글로벌 액션 처리
                new_policy["Sid"] = f"policy-{len(resource_policies) + 1}"  # 고유 Sid 생성
                resource_policies["*"] = new_policy

    # 리소스별로 정책 추가
    for arn, policy in resource_policies.items():
        policies["Statement"].append(policy)

makeField(file_path)
print(json.dumps(policies, indent=4))
