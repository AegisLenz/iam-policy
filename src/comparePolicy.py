import fnmatch

def clustered_compare_policy(user_policies, clustered_policy_by_cloudtrail):
    should_remove_actions = {}
    for userName in clustered_policy_by_cloudtrail.keys():
        if userName == "root":
            user_policy = user_policies.get("root", {})
        else:
            user_policy = user_policies.get(userName, {})
        should_remove_action = comparePolicy(user_policy, clustered_policy_by_cloudtrail[userName])
        
        if userName not in should_remove_actions:
            should_remove_actions[userName] = []
        should_remove_actions[userName].append(should_remove_action)

    return should_remove_actions


def comparePolicy(userPolicy, policy_by_cloudTrail):
    # 삭제해야 할 Action 부분 반환
    least_privilege_action = set()
    should_remove_action = set()

    # CloudTrail 정책에서 최소 권한 액션 수집
    for policy in policy_by_cloudTrail:
        for statement in policy.get("PolicyDocument", {}).get("Statement", []):
            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            for action in actions:
                least_privilege_action.add(action)
    
    # 사용자 정책과 최소 권한 액션 비교
    for policy in userPolicy:
        policy_document = policy.get("PolicyDocument",{})
        for statement in policy_document.get("Statement",[]):
            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            for action in actions:
                matched = any(
                    fnmatch.fnmatch(action, least_action) or least_action == '*'
                    for least_action in least_privilege_action
                )
                if not matched:
                    should_remove_action.add(action)

    return should_remove_action