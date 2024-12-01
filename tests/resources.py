from src.modules.resources.models import ResourceInDb, RoomType


def test_create(client_admin):
    resource_data = {"name": "SuperDesk", "location": "FRANCE", "capacity": 5, "room_type": RoomType.DESK}
    response = client_admin.post("/resources/", json=resource_data)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "superdesk"
    assert data["location"] == "france"
    assert data["capacity"] == 5
    assert data["room_type"] == RoomType.DESK.value
    assert data["id"] is not None

    # Cannot create 2 resources with same email
    response = client_admin.post("/resources/", json=resource_data)
    assert response.status_code == 400


def test_list(session, client_user):
    response = client_user.get("/resources/")
    assert response.status_code == 200
    # Because of fixtures
    resource_count = len(response.json())

    resource_1 = ResourceInDb(name="resource1")
    resource_2 = ResourceInDb(name="resource2")
    session.add(resource_1)
    session.add(resource_2)
    session.commit()
    session.refresh(resource_1)
    session.refresh(resource_2)

    response = client_user.get("/resources/")
    assert response.status_code == 200
    assert len(response.json()) == resource_count + 2


def test_get(session, client_user, resource):
    response = client_user.get("/resources/9999")
    assert response.status_code == 404

    response = client_user.get(f"/resources/{resource.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == resource.id
    assert data["name"] == resource.name
    assert data["location"] == resource.location
    assert data["capacity"] == resource.capacity
    assert data["room_type"] == resource.room_type.value


def test_delete(session, client_admin, resource):
    response = client_admin.delete("/resources/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/resources/{resource.id}")
    assert response.status_code == 204
    assert not session.get(ResourceInDb, resource.id)