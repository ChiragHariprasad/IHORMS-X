import pytest

SUPER_ADMIN = "super_admin"
ORG_ADMIN = "org_admin"
BRANCH_ADMIN = "branch_admin"
DOCTOR = "doctor"
NURSE = "nurse"
RECEPTIONIST = "receptionist"
PHARMACY_STAFF = "pharmacy_staff"
PATIENT = "patient"

ENDPOINTS = [
    ("post", "/api/auth/logout", [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT], None, None),
    ("get",  "/api/auth/me",     [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT], None, None),

    ("post", "/api/super-admin/organizations",               [SUPER_ADMIN], None, None),
    ("get",  "/api/super-admin/organizations",               [SUPER_ADMIN], None, None),
    ("get",  "/api/super-admin/organizations/1",             [SUPER_ADMIN], None, None),
    ("put",  "/api/super-admin/organizations/1/status",      [SUPER_ADMIN], None, None),
    ("get",  "/api/super-admin/analytics/platform",          [SUPER_ADMIN], None, None),
    ("get",  "/api/super-admin/org-admins/1",                [SUPER_ADMIN], None, None),
    ("post", "/api/super-admin/org-admins/1/reset-password", [SUPER_ADMIN], None, None),

    ("get",  "/api/doctor/appointments",                     [DOCTOR], {"status": "SCHEDULED"}, None),
    ("get",  "/api/doctor/patients/search",                  [DOCTOR], {"patient_uid": "DUMMY"}, None),
    ("get",  "/api/doctor/patients/1/history",               [DOCTOR], None, None),

    ("get",  "/api/branches",                                [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT], None, None),
    ("get",  "/api/rooms",                                   [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT], None, None),
    ("get",  "/api/equipment",                               [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT], None, None),
]

ALL_ROLES = [SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, DOCTOR, NURSE, RECEPTIONIST, PHARMACY_STAFF, PATIENT]


@pytest.mark.parametrize("method,url,allowed_roles,query_params,json_body", ENDPOINTS)
def test_endpoint_requires_auth(client, method, url, allowed_roles, query_params, json_body):
    res = client.request(method.upper(), url, params=query_params, json=json_body)
    assert res.status_code in (401, 403)


@pytest.mark.parametrize("method,url,allowed_roles,query_params,json_body", ENDPOINTS)
def test_endpoint_accepts_allowed_roles(client, auth_header_factory, method, url, allowed_roles, query_params, json_body):
    """
    Allowed role should NOT be blocked by RBAC.
    BUT response can be 200/404/422 depending on DB + payload.
    """
    role = allowed_roles[0]
    headers = auth_header_factory(role)

    res = client.request(method.upper(), url, headers=headers, params=query_params, json=json_body)

    assert res.status_code != 403, f"RBAC blocked allowed role={role} on {method.upper()} {url}. Body={res.text}"


@pytest.mark.parametrize("method,url,allowed_roles,query_params,json_body", ENDPOINTS)
def test_endpoint_rejects_disallowed_roles(client, auth_header_factory, method, url, allowed_roles, query_params, json_body):
    disallowed = [r for r in ALL_ROLES if r not in allowed_roles]
    if not disallowed:
        pytest.skip("All roles allowed")

    headers = auth_header_factory(disallowed[0])
    res = client.request(method.upper(), url, headers=headers, params=query_params, json=json_body)

    assert res.status_code == 403, f"{method.upper()} {url} should be forbidden for role={disallowed[0]}. Body={res.text}"
