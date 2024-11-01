import json
import re
import os


def ec2_map_resource(policy_data, log):
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
        "parameter_name": log.get("requestParameters", {}).get("Name") if log.get("requestParameters") else None,
        "instance_id": (
            log.get("requestParameters", {}).get("InstanceId") or  # 단일 인스턴스 ID가 있을 경우
            (log.get("requestParameters", {}).get("instancesSet", {}).get("items", [{}])[0].get("instanceId") if log.get("requestParameters", {}).get("instancesSet") else None) or
            (log.get("responseElements", {}).get("instancesSet", {}).get("items", [{}])[0].get("instanceId") if log.get("responseElements", {}).get("instancesSet") else None)
        )

    }

    resource_list = []
    resources = log.get('resources', [])
    # 리소스 필드에 ARN이 있는지 확인
    if resources:
        for resource in resources:
            if 'ARN' in resource:
                resource_list.append(resource['ARN'])
                return resource_list
    
    # 정책 데이터의 리소스를 순회하며 로그에서 추출한 값을 사용해 리소스를 매핑
    for statement in policy_data.get("policy", []):
        for i, resource in enumerate(statement.get("Resource", [])):
            for key, value in mapping.items():
                if value:
                    resource = resource.replace(f"{{{key}}}", value)
            resource_list.append(resource)

    # 지원되지 않는 이벤트에 대한 기본 리소스 설정
    if not resource_list:
        resource_list.append("*")
    
    return resource_list    


# Step 3: 최소 권한 정책 생성 함수
def generate_least_privilege_policy(policy_data, resource_list):
    least_privilege_policies = []
    for statement in policy_data.get("policy", []):
        actions = statement.get("Action", [])
        for resource in resource_list:
            policy_template = {
                "Action": actions,
                "Resource": [resource],
                "Effect": "Allow",
                "Sid": f"policy-{resource}"
            }
            least_privilege_policies.append(policy_template)
    return least_privilege_policies


# Step 4: EC2 정책 템플릿 로드 및 최소 권한 정책 생성 함수
def ec2_policy_mapper(log, policy_data):
    # 로그에서 필요한 필드 추출 및 리소스 매핑
    resource_list = ec2_map_resource(policy_data, log)
    
    # 최소 권한 정책 생성
    least_privilege_policies = generate_least_privilege_policy(policy_data, resource_list)
    
    # 최종 정책 구성 및 저장
    final_policy = {
        "Version": "2012-10-17",
        "Statement": least_privilege_policies
    }

    return final_policy
