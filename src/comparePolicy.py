import fnmatch
def comparePolicy(userPolicy, policy_by_cloudTrail):
    # 삭제해야 할 Action 부분 반환
    least_privilege_action = set()
    should_remove_action = set()

    # CloudTrail 정책에서 최소 권한 액션 수집
    for statement in policy_by_cloudTrail.get("Statement", []):
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        for action in actions:
            least_privilege_action.add(action)
    
    # 사용자 정책과 최소 권한 액션 비교
    for statement in userPolicy.get("Statement", []):
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