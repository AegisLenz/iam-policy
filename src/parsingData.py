import json
#file_path = "D:\\bob\\AegisLenz\\dataset\\test\\s3bucketTest.json"


class DataField:
    def __init__(self, eventName,eventSource, userIdentity , resources,errorCode ):
        self.eventName = eventName
        self.eventSource =eventSource
        self.userIdentity = userIdentity
        self.resources = resources
        self.errorCode = errorCode

    def returnJson(self):
        return {
            "eventName": self.eventName,
            "eventSource":self.eventSource,
            "userIdentity": self.userIdentity,
            "resources": self.resources,
            "errorCode": self.errorCode
        }
    
def parsingData(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return []

    records = data.get("Records", [])

    extracted_data_list = []

    for record in records:
        extracted_data = DataField(
            eventName=record.get("eventName"),
            eventSource=record.get("eventSource"),
            userIdentity=record.get("userIdentity"),
            resources=record.get("resources"),
            errorCode=record.get("errorCode")
        )
        extracted_data_list.append(extracted_data.returnJson())

    return extracted_data_list
#extracted_data_list = parsingData(file_path)
#print(json.dumps(extracted_data_list, indent=4))