# ec2_policy_mapper.py
from common_utils import load_json, generate_least_privilege_policy

def ec2_map_resource(policy_data, log):
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
            log.get("requestParameters", {}).get("InstanceId") or
            (log.get("requestParameters", {}).get("instancesSet", {}).get("items", [{}])[0].get("instanceId")
             if log.get("requestParameters") and isinstance(log.get("requestParameters").get("instancesSet"), dict) else None) or
            (log.get("responseElements", {}).get("instancesSet", {}).get("items", [{}])[0].get("instanceId")
             if log.get("responseElements") and isinstance(log.get("responseElements").get("instancesSet"), dict) else None)
        ),
        "snap_id": log.get("requestParameters", {}).get("SnapshotId") if log.get("requestParameters") else None,
        "snapshot_id": log.get("requestParameters", {}).get("SnapshotId") if log.get("requestParameters") else None,
        "transit_gateway_route_table_id": log.get("requestParameters", {}).get("TransitGatewayRouteTableId") if log.get("requestParameters") else None,    
        "vpn_gateway_id": log.get("requestParameters", {}).get("VpnGatewayId") if log.get("requestParameters") else None,
        "capacity_reservation_id": log.get("requestParameters", {}).get("CapacityReservationId") if log.get("requestParameters") else None,
        "dedicated_host_id": log.get("requestParameters", {}).get("HostId") if log.get("requestParameters") else None,
        "prefix_list_id": log.get("requestParameters", {}).get("PrefixListId") if log.get("requestParameters") else None,
        "vpc_flow_log_id": log.get("requestParameters", {}).get("FlowLogId") if log.get("requestParameters") else None,
        "reserved_instances_id": log.get("requestParameters", {}).get("ReservedInstancesId") if log.get("requestParameters") else None,
        "spot_fleet_request_id": log.get("requestParameters", {}).get("SpotFleetRequestId") if log.get("requestParameters") else None,
        "traffic_mirror_filter_id": log.get("requestParameters", {}).get("TrafficMirrorFilterId") if log.get("requestParameters") else None,
        "traffic_mirror_session_id": log.get("requestParameters", {}).get("TrafficMirrorSessionId") if log.get("requestParameters") else None,
        "traffic_mirror_filter_rule_id": log.get("requestParameters", {}).get("TrafficMirrorFilterRuleId") if log.get("requestParameters") else None,
        "traffic_mirror_target_id": log.get("requestParameters", {}).get("TrafficMirrorTargetId") if log.get("requestParameters") else None,
        "internet_gateway_id": log.get("requestParameters", {}).get("InternetGatewayId") if log.get("requestParameters") else None,
        "transit_gateway_id": log.get("requestParameters", {}).get("TransitGatewayId") if log.get("requestParameters") else None,
        "vpn_connection_id": log.get("requestParameters", {}).get("VpnConnectionId") if log.get("requestParameters") else None,
        "certificate_authority_id": log.get("requestParameters", {}).get("CertificateAuthorityId") if log.get("requestParameters") else None,
        "bundle_task_id": log.get("requestParameters", {}).get("BundleId") if log.get("requestParameters") else None,
        "network_acl_id": log.get("requestParameters", {}).get("NetworkAclId") if log.get("requestParameters") else None,
        "reserved_instances_listing_id": log.get("requestParameters", {}).get("ReservedInstancesListingId") if log.get("requestParameters") else None,
        "traffic_mirror_filtert_id": log.get("requestParameters", {}).get("TrafficMirrorFiltertId") if log.get("requestParameters") else None
    }

    resource_list = []
    resources = log.get('resources', [])
    if resources:
        for resource in resources:
            if 'ARN' in resource:
                resource_list.append(resource['ARN'])
                return resource_list

    for statement in policy_data.get("policy", []):
        for resource in statement.get("Resource", []):
            original_resource = resource
            for key, value in mapping.items():
                if value:
                    resource = resource.replace(f"{{{key}}}", value)

            if "{" in resource and "}" in resource:
                resource_list.append("*")
            else:
                resource_list.append(resource)
    
    return resource_list    

def ec2_policy_mapper(log, policy_data):
    resource_list = ec2_map_resource(policy_data, log)
    actions = policy_data.get("policy", [{}])[0].get("Action", [])
    least_privilege_policies = generate_least_privilege_policy(actions, resource_list)

    final_policy = {
        "Version": "2012-10-17",
        "Statement": least_privilege_policies
    }
    return final_policy
