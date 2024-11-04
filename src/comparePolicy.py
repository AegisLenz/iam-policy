
#사용자측에서 지워야할 권한 및 리소스 변경사항 반환
def comparePolicy(userPolicy, policy_by_cloudTrail):
    #삭제해야할 Action 부분 반환
    least_priviledge_action = set()
    should_remove_action = set()

    for statement in policy_by_cloudTrail.get("Statement"):
        actions = statement.get("Action")
        for action in actions:
            least_priviledge_action.add(action)
    
    for statement in userPolicy.get("Statement"):
        action = statement.get("Action")
        for action in actions:
            if action not in least_priviledge_action:
                should_remove_action.add(action)

    return should_remove_action
    #변경된 Resource 반환
    #changed_resource = set()
    #for statement_by_cloudTrail in policy_by_cloudTrail.get("Statement"):
     #   action = statement_by_cloudTrail.get("Action")
     #   for statement_by_user in userPolicy.get("Statement"):
            
            




