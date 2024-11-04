# AWS 최소권한 정책 생성하기

AWS CloudTrail Log를 분석하여 사용자에게 적합한 최소권한 정책을 생성하는 도구입니다. 이 프로젝트는 사용자의 활동을 기반으로 최소한의 권한만을 부여함으로써 보안을 강화하는 것을 목표로 합니다.

## 기본 설정

1. eventName과 최소 Action이 맵핑되어 있는 DataBase
2. CloudTrail Log json 파일

## 코드 설명

<<<<<<< HEAD

# AWS 최소권한 정책 생성하기

AWS CloudTrail Log를 분석하여 사용자에게 알맞는 최소권한 정책을 생성합니다.

## 기본 설정

1. eventName과 최소 Action이 맵핑되어 있는 DataBase
2. CloudTrail Log json 파일

## 코드 설명

1. common_utils.py: JSON 파일 로드, 리소스 추출, 최소 권한 정책 생성, 정책 병합 등의 공통 기능을 제공하는 유틸리티 코드.
2. comparePolicy.py: 사용자의 정책과 CloudTrail Log로 생성된 최소 권한 정책을 비교하여 불필요한 권한을 식별하고 반환하는 코드.
3. ec2_policy_mapper.py: EC2 관련 로그에서 필요한 resource를 추출하고, 최소 권한 정책을 생성하는 코드.
4. s3_policy_mapper.py: S3 관련 로그에서 필요한 resource를 추출하고, 최소 권한 정책을 생성하는 코드.
5. iam_policy_mapper.py: IAM 관련 로그에서 필요한 리소스를 추출하고, 최소 권한 정책을 생성하는 코드.
6. extract_policy_by_cloudTrail.py: 여러 정책을 병합하여 최종 최소 권한 정책을 생성하는 코드.
7. main.py: 최종적으로 실행하는 코드로, CloudTrail 로그를 로드하고, 이벤트와 리소스를 매핑하여 최종 최소 권한 정책을 생성하고, 필요시 기존 사용자 정책과 비교하여 불필요한 액션을 제거하는 코드.

## 실행 방법

아래 두 경로를 지정한 후에 main.py 실행

- eventName과 최소 Action이 맵핑되어 있는 DataBase의 경로
- CloudTrail Log json 파일의 경로
