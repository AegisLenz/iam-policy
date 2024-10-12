# AWS 최소권한 정책 생성하기
AWS CloudTrail Log를 분석하여 사용자에게 알맞는 최소권한 정책을 생성합니다.

## 기본 설정
1. eventName과 최소 Action이 맵핑되어 있는 DataBase
2. CloudTrail Log json 파일

## 코드 설명
1. cloudtrail_parser.py: CloudTrail 로그에서 필요한 정보를 추출하여 후속 작업에 사용할 수 있도록 데이터를 정리하는 코드
2. policy_handler.py: 특정 이벤트(S3, EC2)의 정책 템플릿을 로드하고, 로그 항목에 따라 필요한 리소스를 생성하는 코드
3. policy_mapper.py: CloudTrail 로그에서 추출된 데이터를 바탕으로 리소스와 액션을 매핑하여 정책을 생성하는 코드
4. main.py: CloudTrail 로그를 로드하고, 이벤트와 리소스를 매핑하여 최종 정책을 생성하고 파일로 저장하는 코드.

## 실행 방법
아래 두 경로를 지정한 후에 실행
* eventName과 최소 Action이 맵핑되어 있는 DataBase의 경로
* CloudTrail Log json 파일의 경로
