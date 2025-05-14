

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_admin_profile_update_success(client):
    """
    Test case 1: Cập nhật thông tin thành công với mật khẩu mới
    """
    user = User.objects.create_user(username="admin", password="adminpass", user_type=1)
    client.login(username="admin", password="adminpass")

    url = reverse("admin_profile_update")
    data = {
        "first_name": "NewFirst",
        "last_name": "NewLast",
        "password": "newpass123"
    }

    response = client.post(url, data, follow=True)

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.first_name == "NewFirst"
    assert user.last_name == "NewLast"
    assert user.check_password("newpass123")


@pytest.mark.django_db
def test_admin_profile_update_without_password(client):
    """
    Test case 2: Cập nhật thông tin mà không thay đổi mật khẩu
    """
    user = User.objects.create_user(username="admin", password="adminpass", user_type=1)
    old_hashed_password = user.password
    client.login(username="admin", password="adminpass")

    url = reverse("admin_profile_update")
    data = {
        "first_name": "OnlyName",
        "last_name": "Changed",
        "password": ""
    }

    response = client.post(url, data)
    user.refresh_from_db()
    assert user.first_name == "OnlyName"
    assert user.last_name == "Changed"
    assert user.password == old_hashed_password  # password không đổi


@pytest.mark.django_db
def test_admin_profile_update_invalid_method(client):
    """
    Test case 3: Gửi request bằng GET (không hợp lệ)
    """
    user = User.objects.create_user(username="admin", password="adminpass", user_type=1)
    client.login(username="admin", password="adminpass")

    url = reverse("admin_profile_update")
    response = client.get(url)

    assert response.status_code == 302  # Bị redirect về admin_profile
    assert response.url == reverse("admin_profile")

#  2 fail, 1 pass

