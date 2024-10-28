import json
import re
import os

def map_resource(policy_data, log):
    #리소스 매핑 필드 정의
    mapping = {
        "account_id": log.get("userIdentity").get("accountId") if log.get("userIdentity") else None,
        "peering_connection_id": log.get("responseElements", {}).get("vpcPeeringConnectionId") if log.get("responseElements") else None,
        "vpc_id": log.get("vpcId", ""),
        "region": log.get("awsRegion"),
        "transit_gateway_multicast_domain_id": log.get("requestParameters", {}).get("TransitGatewayMulticastDomainId") if log.get("requestParameters") else None,
        "service_id": log.get("requestParameters", {}).get("ServiceId") if log.get("requestParameters") else None,
        "security_group_id": log.get("requestParameters", {}).get("securityGroupIds", [])[0] if log.get("requestParameters", {}).get("securityGroupIds") else None,
        "client_vpn_endpoint_id": log.get("requestParameters", {}).get("ClientVpnEndpointId") if log.get("requestParameters") else None,
        "host_id": log.get("requestParameters", {}).get("hostIds", [])[0] if log.get("requestParameters", {}).get("hostIds") else None,
        "bucket_name": log.get("requestParameters", {}).get("BucketName") if log.get("requestParameters") else None,
        "attachment_id": log.get("requestParameters", {}).get("TransitGatewayAttachmentId") if log.get("requestParameters") else None,
        "route_table_id": log.get("requestParameters", {}).get("RouteTableId") if log.get("requestParameters") else None,
        "subnet_id": log.get("requestParameters", {}).get("SubnetId") if log.get("requestParameters") else None,
        "instance_id": log.get("requestParameters", {}).get("InstanceId") if log.get("requestParameters") else None,
        "volume_id": log.get("requestParameters", {}).get("VolumeId") if log.get("requestParameters") else None,
        "image_id": log.get("requestParameters", {}).get("ImageId") if log.get("requestParameters") else None,
        "launch_template_id": log.get("requestParameters", {}).get("LaunchTemplateId") if log.get("requestParameters") else None,
        "key_pair_name": log.get("requestParameters", {}).get("KeyName") if log.get("requestParameters") else None,
        "ipv6_pool_id": log.get("requestParameters", {}).get("Ipv6PoolId") if log.get("requestParameters") else None,
        "coip_pool_id": log.get("requestParameters", {}).get("CoipPoolId") if log.get("requestParameters") else None,
        "allocation_id": log.get("requestParameters", {}).get("AllocationId") if log.get("requestParameters") else None,
        "instance_profile_name": log.get("requestParameters", {}).get("IamInstanceProfile", {}).get("Arn") if log.get("requestParameters") and log.get("requestParameters", {}).get("IamInstanceProfile") else None,
        "local_gateway_route_table_id": log.get("requestParameters", {}).get("LocalGatewayRouteTableId") if log.get("requestParameters") else None,
        "network_interface_id": log.get("requestParameters", {}).get("NetworkInterfaceId") if log.get("requestParameters") else None,
        "object_key": log.get("requestParameters", {}).get("Key") if log.get("requestParameters") else None,
        "customer_gateway_id": log.get("requestParameters", {}).get("CustomerGatewayId") if log.get("requestParameters") else None,
        "parameter_name": log.get("requestParameters", {}).get("Name") if log.get("requestParameters") else None
    }

    for statement in policy_data.get("policy", []):
        for i, resource in enumerate(statement.get("Resource", [])):
            for key, value in mapping.items():
                if value is not None:  
                    resource = resource.replace(f"{{{key}}}", str(value))
            statement["Resource"][i] = resource

def load_json(file_path):
    try:
        with open(file_path,'r') as file:
            data = json.load(file)

            # CloudTrail 로그 파일인 경우 "Records" 필드를 반환
            if "Records" in data:
                return data.get("Records", [])
            # 정책 파일인 경우 그대로 반환
            return data
        
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None

def save_mapped_policy(policy_data, output_path):
    try:
        with open(output_path, 'w') as file:
            json.dump(policy_data, file, indent=4)
        print(f"Mapped policy saved to {output_path}")
    except IOError:
        print(f"Error: Could not write to file {output_path}")

def main():
    log_path = './ex.json'
    database_path = './../AWSDatabase/EC2'
    output_path ='./'
    logs = load_json(log_path)
    policy_path = database_path

    if logs is not None:
        for log in logs:
            eventName = log.get("eventName")

            policy_path += f'/{eventName}.json'
            policy = load_json(policy_path)

            if policy is not None:
                map_resource(policy, log)
                print("Mapped Policy:", json.dumps(policy, indent=4))

            # 매핑된 정책을 새로운 파일로 저장
                #mapped_policy_path = os.path.join(output_path, f"{eventName}_mapped.json")
                #save_mapped_policy(policy, mapped_policy_path)

if __name__ == "__main__":
    main()
