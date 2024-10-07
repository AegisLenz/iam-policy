#cloudTrail에서 eventName, eventSource, userIdentity, resources, errorCode를 추출하는 코드
import json

# 이벤트 데이터를 나타내는 클래스
class DataField:
    def __init__(self, eventName, eventSource, userIdentity, resources, errorCode):
        self.eventName = eventName
        self.eventSource = eventSource
        self.userIdentity = userIdentity
        self.resources = resources
        self.errorCode = errorCode

    def return_json(self):
        return {
            "eventName": self.eventName,
            "eventSource": self.eventSource,
            "userIdentity": self.userIdentity,
            "resources": self.resources,
            "errorCode": self.errorCode
        }

# CloudTrail 로그를 파싱하고 필요한 데이터를 추출하는 함수
def parsing_data(cloudTrail_Log_filepath):
    try:
        # JSON 파일을 읽어서 파싱
        with open(cloudTrail_Log_filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)  # JSON 데이터를 파싱하여 리스트로 변환
    except FileNotFoundError:
        print(f"File not found: {cloudTrail_Log_filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {cloudTrail_Log_filepath}")
        return []

    extracted_data_list = []

    # 각 레코드에서 필요한 필드를 추출
    if isinstance(data, list):  # data가 리스트인지 확인
        for record in data:
            resources = []
            if 'resources' in record:
                # 리소스가 존재하면 ARN을 추출
                resources = [res.get("ARN", "N/A") for res in record.get("resources", [])]

            extracted_data = DataField(
                eventName=record.get("eventName", "N/A"),
                eventSource=record.get("eventSource", "N/A"),
                userIdentity=record.get("userIdentity", {}).get("arn", "N/A"),
                resources=resources,
                errorCode=record.get("errorCode", "N/A")
            )
            extracted_data_list.append(extracted_data.return_json())
    else:
        print("Unexpected JSON format: expected a list of records.")

    return extracted_data_list

# 외부에서 사용할 수 있도록 parsingData 함수 제공
def parsingData(file_path):
    return parsing_data(file_path)


