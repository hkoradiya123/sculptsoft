from fastapi import Depends, HTTPException, status


ROLE_PERMISSIONS = {
    "admin": [
        "create_user",
        "delete_user",
        "view_dashboard",
        "manage_products",
    ],
    "seller": ["manage_products", "view_dashboard"],
    "user": ["view_dashboard"],
}


def get_permissions(roles: list[str]):
    permissions: list[str] = []

    for role in roles:
        for permission in ROLE_PERMISSIONS.get(role, []):
            if permission not in permissions:
                permissions.append(permission)

    return permissions


def require_permissions(*required_permissions: str):
    from app.auth.dependencies import verify_token

    def checker(user=Depends(verify_token)):
        user_permissions = user.get("permissions", [])

        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )

        return user

    return checker
