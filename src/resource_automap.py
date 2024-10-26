import json
import re
import os

def generate_policy_template(policy_data):
    """
    입력된 정책 데이터를 템플릿 형식으로 변환하는 함수입니다.
    """
    patterns = {
        "region": r"(?<=:)(\*|\w+-\w+-\d+)(?=:)",  # 리전 패턴
        "account_id": r"002677082836",  # 계정 ID 고정 값 -> {account_id}로 변환
        "certificate_id": r"certificate/([a-f0-9-]+)",  # ACM 인증서 ID
        "role_name": r"role/([\w+=,.@-]+)",  # IAM 역할 이름
        "vpc_endpoint_id": r"vpc-endpoint/(vpce-\w+)",  # VPC 엔드포인트 ID
        "service_id": r"vpc-endpoint-service/(vpce-svc-\w+)",  # VPC 엔드포인트 서비스 ID
        "attachment_id": r"transit-gateway-attachment/(tgw-attach-\w+)",  # Transit Gateway Attachment ID
        "peering_connection_id": r"vpc-peering-connection/(pcx-\w+)",  # VPC 피어링 연결 ID
        "vpc_id": r"vpc/(vpc-\w+)",  # VPC ID
        "security_group_id": r"security-group/(sg-\w+)",  # 보안 그룹 ID
        "client_vpn_endpoint_id": r"client-vpn-endpoint/(cvpn-endpoint-\w+)",  # 클라이언트 VPN 엔드포인트 ID
        "network_interface_id": r"network-interface/(eni-\w+)",  # 네트워크 인터페이스 ID
        "instance_id": r"instance/(i-\w+)",  # EC2 인스턴스 ID
        "allocation_id": r"elastic-ip/(eipalloc-\w+)",  # Elastic IP 할당 ID
        "route_table_id": r"route-table/(rtb-\w+)",  # 라우트 테이블 ID
        "subnet_id": r"subnet/(subnet-\w+)"  # 서브넷 ID
    }

    template_policy = []

    # JSON 데이터가 리스트인 경우 첫 번째 요소만 사용
    if isinstance(policy_data, list):
        policy_data = policy_data[0]

    # 정책 데이터의 Statement 부분 순회
    for statement in policy_data.get('policy', {}).get('Statement', []):
        action = statement.get('Action', [])
        effect = statement.get('Effect', 'Allow')
        resources = []

        # 리소스 템플릿화 처리
        for resource in statement.get('Resource', []):
            resource_template = resource  # 기본 리소스를 복사
            for key, pattern in patterns.items():
                # 계정 ID 고정 값 처리
                if key == "account_id":
                    resource_template = resource_template.replace(pattern, "{account_id}")
                else:
                    # 정규 표현식을 사용해 템플릿화
                    resource_template = re.sub(pattern, f"{{{key}}}", resource_template)
            resources.append(resource_template)

        template_policy.append({
            "Action": action,
            "Effect": effect,
            "Resource": resources
        })

    return {"policy": template_policy}

def load_policy_from_file(file_path):
    """
    JSON 파일을 로드하는 함수.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_template_to_file(template, output_path):
    """
    템플릿화된 정책을 파일로 저장하는 함수.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(template, file, indent=4, ensure_ascii=False)

def process_all_json_files_in_folder(folder_path):
    """
    주어진 폴더의 모든 JSON 파일을 순회하며 템플릿을 생성합니다.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            input_file_path = os.path.join(folder_path, filename)
            output_file_path = os.path.join(folder_path, filename.replace(".json", "_template.json"))

            try:
                policy_data = load_policy_from_file(input_file_path)
                template = generate_policy_template(policy_data)

                save_template_to_file(template, output_file_path)
                print(f"템플릿 파일이 '{output_file_path}' 경로에 저장되었습니다.")
            except Exception as e:
                print(f"오류 발생: {input_file_path} 처리 중 문제 발생 - {e}")

# 실행 예시: 폴더 경로 설정
folder_path = r"C:\Users\yjeongc\Downloads\iam-policy\AWSDatabase\EC2\test"

if __name__ == "__main__":
    process_all_json_files_in_folder(folder_path)