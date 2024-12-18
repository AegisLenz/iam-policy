import requests
from bs4 import BeautifulSoup
import json
import re
import os

def extract_service_prefix(soup):
    """
    HTML 내의 <p> 태그에서 'service prefix:'를 찾아 서비스 접두사를 추출합니다.
    """
    service_prefix = ''

    # 모든 <p> 태그 검색
    p_tags = soup.find_all('p')
    for p in p_tags:
        if 'service prefix:' in p.text.lower():
            code_tag = p.find('code')
            if code_tag:
                service_prefix = code_tag.text.strip()
                break

    return service_prefix

def infer_service_prefix_from_url(url):
    """
    URL에서 서비스 접두사를 유추합니다.
    예: 'https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonaioperations.html'
    → 'amazonaioperations'
    """
    match = re.search(r'/list_(.+)\.html', url)
    if match:
        service_prefix = match.group(1)
        # 언더스코어(_)를 제거하거나 다른 변환이 필요할 경우 추가
        service_prefix = service_prefix.replace('_', '')
        return service_prefix
    return 'unknown_service'

def find_actions_table(soup):
    """
    지정된 헤더를 포함하는 테이블을 HTML 내에서 찾아 반환합니다.
    """
    required_headers = [
        'actions', 
        'description', 
        'access level', 
        'resource types (*required)', 
        'condition keys', 
        'dependent actions'
    ]

    # 모든 <table> 태그 검색
    tables = soup.find_all("table")
    for tbl in tables:
        headers = tbl.find_all("th")
        header_text = [th.get_text(strip=True).lower() for th in headers]
        
        # 테이블의 헤더가 필요한 모든 항목을 포함하는지 확인
        if all(req in header_text for req in required_headers):
            return tbl

    return None

def extract_actions(table):
    """
    액션 테이블에서 액션 이름들을 추출하여 리스트로 반환합니다.
    """
    actions = []
    current_action = None

    # 테이블의 모든 행(<tr>) 찾기, 첫 번째 행은 헤더이므로 제외
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue  # 빈 행은 건너뜁니다.

        # 첫 번째 열에 액션 이름이 있는지 확인
        action_td = cols[0]
        a_tag = action_td.find("a")
        if a_tag:
            action_name = a_tag.text.strip()
            actions.append(action_name)
            current_action = action_name  # 현재 액션을 갱신
        else:
            # 이전 액션을 유지 (rowspan으로 인한 빈 셀)
            if current_action:
                actions.append(current_action)

    # 중복 제거
    unique_actions = list(dict.fromkeys(actions))
    return unique_actions

def main():
    # 처리할 URL 리스트
    urls = [
        "https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsaccountmanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsactivate.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonaioperations.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_alexaforbusiness.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmediaimport.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsamplify.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsamplifyadmin.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsamplifyuibuilder.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_apachekafkaapisforamazonmskclusters.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonapigateway.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonapigatewaymanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonapigatewaymanagementv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappmesh.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappmeshpreview.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapprunner.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappstudio.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapp2container.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappconfig.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappfabric.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonappflow.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonappintegrations.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationautoscaling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationcostprofilerservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_applicationdiscoveryarsenal.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationdiscoveryservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationmigrationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonapplicationrecoverycontroller-zonalshift.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationtransformationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonappstream2.0.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsappsync.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsartifact.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonathena.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsauditmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonauroradsql.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsautoscaling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsb2bdatainterchange.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbackup.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbackupgateway.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbackupstorage.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbatch.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbilling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbillingandcostmanagementdataexports.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbillingandcostmanagementpricingcalculator.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbillingconductor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbillingconsole.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbraket.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbudgetservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsbugbust.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscertificatemanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awschatbot.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonchime.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscleanrooms.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscleanroomsml.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudcontrolapi.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonclouddirectory.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudmap.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloud9.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudformation.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudfront.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudfrontkeyvaluestore.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudhsm.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudsearch.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudshell.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudtrail.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudtraildata.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatch.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationinsights.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationsignals.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchevidently.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchinternetmonitor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchlogs.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchnetworkmonitor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchobservabilityaccessmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchobservabilityadminservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudwatchrum.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchsynthetics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodeartifact.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodebuild.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodecatalyst.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodecommit.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodeconnections.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodedeploy.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodedeploysecurehostcommandsservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodeguru.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodeguruprofiler.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodegurureviewer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodegurusecurity.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodepipeline.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodestar.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodestarconnections.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscodestarnotifications.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncodewhisperer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitoidentity.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitosync.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitouserpools.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehend.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehendmedical.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscomputeoptimizer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsconfig.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnectcases.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnectcustomerprofiles.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnectoutboundcampaigns.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonconnectvoiceid.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsconnectorservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsconsolemobileapp.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsconsolidatedbilling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscontrolcatalog.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscontroltower.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscostandusagereport.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscostexplorerservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscostoptimizationhub.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscustomerverificationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdataexchange.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondatalifecyclemanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatapipeline.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatabasemigrationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_databasequerymetadataservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatasync.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondatazone.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdeadlinecloud.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdeepcomposer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdeeplens.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdeepracer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondetective.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdevicefarm.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondevopsguru.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdiagnostictools.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdirectconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdirectoryservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdirectoryservicedata.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondocumentdbelasticclusters.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodbacceleratordax.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonec2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonec2autoscaling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonec2imagebuilder.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonec2instanceconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneksauth.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselasticbeanstalk.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticblockstore.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistry.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistrypublic.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselasticdisasterrecovery.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticfilesystem.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticinference.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelastickubernetesservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselasticloadbalancing.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselasticloadbalancingv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticmapreduce.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelastictranscoder.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticache.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalappliancesandsoftware.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalappliancesandsoftwareactivationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediaconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediaconvert.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmedialive.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediapackage.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediapackagev2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediapackagevod.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediastore.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalmediatailor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalsupportcases.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awselementalsupportcontent.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonemroneksemrcontainers.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonemrserverless.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsendusermessagingsmsandvoicev2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsendusermessagingsocial.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsentityresolution.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridge.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgepipes.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgescheduler.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgeschemas.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsfaultinjectionservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonfinspace.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonfinspaceapi.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsfirewallmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonforecast.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonfrauddetector.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsfreetier.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonfreertos.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonfsx.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazongamelift.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsglobalaccelerator.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsglue.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsgluedatabrew.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsgroundstation.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazongroundtruthlabeling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonguardduty.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthapisandnotifications.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthimaging.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthlake.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthomics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonhoneycode.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiamaccessanalyzer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiamidentitycentersuccessortoawssinglesign-on.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiamidentitycentersuccessortoawssinglesign-ondirectory.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiamidentitycenteroidcservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementiam.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementrolesanywhere.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentitystore.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentitystoreauth.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentitysync.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsimportexportdiskservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoninspector.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoninspector2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoninspectorscan.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoninteractivevideoservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoninteractivevideoservicechat.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsinvoicingservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot1-click.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotanalytics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotcoredeviceadvisor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotdevicetester.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotevents.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleethubfordevicemanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleetwise.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotgreengrass.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotgreengrassv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotjobsdataplane.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotsitewise.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiottwinmaker.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotwireless.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiq.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiqpermissions.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkendra.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkendraintelligentranking.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awskeymanagementservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkeyspacesforapachecassandra.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalytics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalyticsv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisdatastreams.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisfirehose.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisvideostreams.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslakeformation.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslambda.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslaunchwizard.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlex.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlexv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslicensemanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslicensemanagerlinuxsubscriptionsmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslicensemanagerusersubscriptions.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlightsail.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlocation.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlocationservicemaps.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlocationserviceplaces.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlocationserviceroutes.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlookoutforequipment.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlookoutformetrics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonlookoutforvision.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmachinelearning.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmacie.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmainframemodernizationapplicationtesting.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmainframemodernizationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedblockchain.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedblockchainquery.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedgrafana.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedserviceforprometheus.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedstreamingforapachekafka.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedstreamingforkafkaconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmanagedworkflowsforapacheairflow.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplace.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacecatalog.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacecommerceanalyticsservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacedeploymentservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacediscovery.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplaceentitlementservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplaceimagebuildingservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacemanagementportal.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacemeteringservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplaceprivatemarketplace.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplaceprocurementsystemsintegration.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacereporting.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacesellerreporting.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmarketplacevendorinsights.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmechanicalturk.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmemorydb.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmessagedeliveryservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmessagegatewayservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmicroserviceextractorfor.net.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmigrationaccelerationprogramcredits.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmigrationhub.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmigrationhuborchestrator.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmigrationhubrefactorspaces.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsmigrationhubstrategyrecommendations.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmobileanalytics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmonitron.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonmq.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonneptune.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonneptuneanalytics.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsnetworkfirewall.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_networkflowmonitor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsnetworkmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsnetworkmanagerchat.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonnimblestudio.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazononeenterprise.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonopensearch.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonopensearchingestion.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonopensearchserverless.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonopensearchservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsopsworks.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsopsworksconfigurationmanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsoutposts.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspanorama.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsparallelcomputingservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspartnercentralaccountmanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspartnercentralselling.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspaymentcryptography.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspayments.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsperformanceinsights.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpersonalize.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpinpoint.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpinpointemailservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpinpointsmsandvoiceservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpolly.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspricelist.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecaconnectorforactivedirectory.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecaconnectorforscep.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecertificateauthority.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatelink.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsproton.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspurchaseordersconsole.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonq.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonqbusiness.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonqbusinessqapps.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonqinconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonqldb.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonquicksight.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrds.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrdsdataapi.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrdsiamauthentication.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrecyclebin.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonredshift.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonredshiftdataapi.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonredshiftserverless.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrekognition.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrepostprivate.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsresiliencehub.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsresourceaccessmanagerram.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsresourceexplorer.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonresourcegrouptaggingapi.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsresourcegroups.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrhelknowledgebaseportal.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrobomaker.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53domains.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53profiles.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53recoverycluster.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53recoverycontrols.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53recoveryreadiness.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53resolver.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3express.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3glacier.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3objectlambda.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3onoutposts.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3tables.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsagemaker.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsagemakerdatascienceassistant.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsagemakergeospatialcapabilities.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsagemakergroundtruthsynthetic.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsagemakerwithmlflow.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssavingsplans.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssecretsmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssecurityhub.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssecurityincidentresponse.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsecuritylake.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssecuritytokenservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsservermigrationservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsserverlessapplicationrepository.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsservicecatalog.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsserviceprovidingmanagedprivatenetworks.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_servicequotas.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonses.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsshield.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssigner.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssignin.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsimpleemailservice-mailmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsimpleemailservicev2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsimpleworkflowservice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsimpledb.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssimspaceweaver.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssnowdevicemanagement.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssnowball.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsns.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssqlworkbench.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsqs.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstepfunctions.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstoragegateway.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupplychain.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupport.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupportappinslack.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupportplans.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssupportrecommendations.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssustainability.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerforsap.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerguiconnect.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanagercontacts.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerquicksetup.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_tageditor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstaxsettings.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstelconetworkbuilder.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontimestream.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontimestreaminfluxdb.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstiros.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranscribe.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstransferfamily.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranslate.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstrustedadvisor.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsusernotifications.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsusernotificationscontacts.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsusersubscriptions.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsverifiedaccess.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonverifiedpermissions.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonvpclattice.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonvpclatticeservices.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awswaf.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awswafregional.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awswafv2.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awswell-architectedtool.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awswickr.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkdocs.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworklink.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkmail.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkmailmessageflow.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkspaces.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkspacesapplicationmanager.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkspacessecurebrowser.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkspacesthinclient.html",
"https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsx-ray.html"
    ]
    
    # 저장할 디렉토리 경로
    output_dir = r"C:\Workspace\iam-policy\RealService"
    
    # 디렉토리가 존재하지 않으면 생성
    os.makedirs(output_dir, exist_ok=True)
    
    for url in urls:
        print(f"Processing URL: {url}")
        
        # HTML 페이지 가져오기
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            continue  # 다음 URL로 넘어감
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. 서비스 접두사 추출
        service_prefix = extract_service_prefix(soup)
        
        if not service_prefix:
            # 접두사를 페이지에서 찾지 못하면 URL에서 유추
            service_prefix = infer_service_prefix_from_url(url)
            print(f"Service prefix not found in page. Inferred service prefix: {service_prefix}")
        else:
            print(f"Service Prefix: {service_prefix}")
        
        # 2. Actions 테이블 찾기
        actions_table = find_actions_table(soup)
        
        if not actions_table:
            print("Actions 테이블을 찾을 수 없습니다.\n")
            continue  # 다음 URL로 넘어감
        
        # 3. 액션 이름 추출
        actions = extract_actions(actions_table)
        
        # 4. JSON 형식으로 데이터 구성
        policy_data = {
            "servicePrefix": service_prefix,
            "AllowActions": actions
        }
        
        # 5. JSON 파일로 저장
        try:
            # 파일명은 서비스 접두사에 기반하여 동적으로 생성
            output_filename = f"{service_prefix}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(policy_data, f, indent=4)
            
            print(f"JSON 데이터가 '{output_path}' 파일로 저장되었습니다.\n")
        except IOError as e:
            print(f"파일 쓰기 중 오류가 발생했습니다: {e}\n")
    
    print("모든 URL 처리가 완료되었습니다.")

if __name__ == "__main__":
    main()
