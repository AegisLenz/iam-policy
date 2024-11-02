# s3_policy_mapper.py
from common_utils import load_json, extract_resource_from_log, generate_least_privilege_policy

def s3_policy_mapper(log, policy_data):
    mapping = {
        "bucket_name": log.get("requestParameters", {}).get("bucketName"),
        "object_key": log.get("requestParameters", {}).get("key"),
        "key_prefix": log.get("requestParameters", {}).get("keyPrefix"),
    }

    resource_arn = f"arn:aws:s3:::{mapping['bucket_name']}"
    if mapping['object_key']:
        resource_arn += f"/{mapping['object_key']}"
    elif mapping['key_prefix']:
        resource_arn += f"/{mapping['key_prefix']}*"

    resource_list = []
    for statement in policy_data.get("policy", []):
        for resource in statement.get("Resource", []):
            for key, value in mapping.items():
                if value:
                    resource = resource.replace(f"{{{key}}}", value)

            if "{" in resource and "}" in resource:
                resource_list.append("*")
            else:
                resource_list.append(resource)

    actions = policy_data.get("policy", [{}])[0].get("Action", [])
    least_privilege_policies = generate_least_privilege_policy(actions, resource_list)

    final_policy = {
        "Version": "2012-10-17",
        "Statement": least_privilege_policies
    }

    return final_policy
