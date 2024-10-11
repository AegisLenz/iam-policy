# AWS 최소권한 정책 생성하기
AWS CloudTrail Log를 분석하여 사용자에게 알맞는 최소권한 정책을 생성합니다.

## 기본 설정
1. eventName과 최소 Action이 맵핑되어 있는 DataBase
2. CloudTrail Log json 파일

## 코드 설명
1. parsingData.py :CloudTrail에서 eventName, eventSource, userIdentity, resources, errorCode를 추출하는 코드
3. ActionMapping.py : eventname과 Action을 맵핑하는 코드
4. MakePolicy : 템플릿을 활용하여 정책을 생성하는 코드

## 실행 방법
아래 두 경로를 지정한 후에 실행
* eventName과 최소 Action이 맵핑되어 있는 DataBase의 경로
* CloudTrail Log json 파일의 경로
