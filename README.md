# AWS 최소권한 정책 생성하기
AWS CloudTrail Log를 분석하여 사용자에게 알맞는 최소권한 정책을 생성합니다.

## 기본 설정
1. eventName과 최소 Action이 맵핑되어 있는 DataBase
2. CloudTrail Log json 파일

## 코드 설명
1. common_utils.py: json파일 로드하는 함수 및 policy들 병합
2. ec2_policy_mapper.py: EC2 이벤트의 정책 템플릿을 로드하고, 로그 항목에 따라 필요한 리소스를 매핑하는 코드
3. s3_policy_mapper.py: S3 이벤트의 정책 템플릿을 로드하고, 로그 항목에 따라 필요한 리소스를 매핑하는 코드
4. iam_policy_mapper.py: IAM 이벤트의 정책 템플릿을 로드하고, 로그 항목에 따라 필요한 리소스를 매핑하는 코드
5. main.py: CloudTrail 로그를 로드하고, 이벤트와 리소스를 매핑하여 최종 정책을 생성하고 파일로 저장하는 코드.

## 실행 방법
아래 두 경로를 지정한 후에 실행
* eventName과 최소 Action이 맵핑되어 있는 DataBase의 경로
* CloudTrail Log json 파일의 경로
