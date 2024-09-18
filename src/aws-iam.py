import boto3
import os
from dotenv import load_dotenv
import json

# .env 파일 로드
load_dotenv()

# 환경 변수에서 자격증명 읽기
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Boto3 세션 생성
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='ap-northeast-2'  # 원하는 리전으로 설정
)

# Boto3 클라이언트 생성 (세션을 통해 생성)
iam_client = session.client('iam')

def get_user_permissions(user_name, iam_client):
    permissions = []
    
    # 1. 관리형 정책 가져오기
    attached_policies = iam_client.list_attached_user_policies(UserName=user_name)
    for policy in attached_policies['AttachedPolicies']:
        policy_arn = policy['PolicyArn']
        permissions.extend(get_policy_permissions(policy_arn, iam_client))
    
    # 2. 인라인 정책 가져오기
    inline_policies = iam_client.list_user_policies(UserName=user_name)
    for policy_name in inline_policies['PolicyNames']:
        inline_policy = iam_client.get_user_policy(UserName=user_name, PolicyName=policy_name)
        permissions.extend(parse_policy_document(inline_policy['PolicyDocument']))
    
    return permissions

def get_policy_permissions(policy_arn, iam_client):
    permissions = []
    
    # 정책 버전 가져오기
    policy = iam_client.get_policy(PolicyArn=policy_arn)
    policy_version = policy['Policy']['DefaultVersionId']
    
    # 정책 문서 가져오기
    policy_document = iam_client.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy_version
    )
    
    # 정책 문서에서 허용된 액션 확인
    permissions.extend(parse_policy_document(policy_document['PolicyVersion']['Document']))
    
    return permissions

def parse_policy_document(policy_document):
    permissions = []
    for statement in policy_document['Statement']:
        effect = statement['Effect']
        actions = statement.get('Action', [])
        resources = statement.get('Resource', [])
        
        # Action이 문자열로 하나만 있을 경우 리스트로 변환
        if isinstance(actions, str):
            actions = [actions]
        
        permissions.append({
            "Effect": effect,
            "Actions": actions,
            "Resources": resources
        })
    
    return permissions

def main():
    # 사용자 이름을 입력하여 정책 가져오기
    user_name = 'raynor-iam_privesc_by_rollback_cgid9uylre8kwi'
    permissions = get_user_permissions(user_name, iam_client)
    print(json.dumps(permissions, indent=4))

if __name__== "__main__":
    main()
