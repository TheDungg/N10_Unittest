

import pytest
from student_management_app.models import CustomUser, FeedBackStaffs

# ✅ Test case 1: Gửi phản hồi thành công cho feedback hợp lệ
@pytest.mark.django_db
def test_staff_feedback_reply_success(client):
    """
    Test case 1: Gửi phản hồi thành công cho feedback hợp lệ.
    Mong đợi: status_code = 200, content = "True", feedback_reply được cập nhật đúng.
    """
    staff_user = CustomUser.objects.create_user(
        username="staff1",
        password="pass123",
        user_type=2
    )
    feedback = FeedBackStaffs.objects.create(
        staff_id=staff_user,
        feedback="Cần hỗ trợ điểm danh",
        feedback_reply=""
    )

    response = client.post("/staff_feedback_message_reply/", {
        "id": feedback.id,
        "reply": "Đã xử lý xong"
    })

    feedback.refresh_from_db()
    assert response.status_code == 200
    assert response.content == b"True"
    assert feedback.feedback_reply == "Đã xử lý xong"


# ✅ Test case 2: Gửi phản hồi với ID không tồn tại
@pytest.mark.django_db
def test_staff_feedback_reply_invalid_id(client):
    """
    Test case 2: Gửi phản hồi với ID không tồn tại.
    Mong đợi: status_code = 200, content = "False".
    """
    response = client.post("/staff_feedback_message_reply/", {
        "id": 9999,
        "reply": "Nội dung"
    })

    assert response.status_code == 200
    assert response.content == b"False"


# ✅ Test case 3: Gửi POST nhưng thiếu cả id và reply
@pytest.mark.django_db
def test_staff_feedback_reply_missing_fields(client):
    """
    Test case 3: Gửi POST nhưng thiếu cả 'id' và 'reply'.
    Mong đợi: status_code = 200, content = "False".
    """
    response = client.post("/staff_feedback_message_reply/", {})

    assert response.status_code == 200
    assert response.content == b"False"


# ✅ Test case 4: Gửi phản hồi nhưng nội dung reply rỗng
@pytest.mark.django_db
def test_staff_feedback_reply_empty_reply(client):
    """
    Test case 4: Gửi phản hồi nhưng nội dung reply rỗng.
    Mong đợi: status_code = 200, feedback_reply vẫn được lưu rỗng.
    """
    staff_user = CustomUser.objects.create_user(username="staff2", password="123", user_type=2)
    feedback = FeedBackStaffs.objects.create(
        staff_id=staff_user,
        feedback="Test empty reply",
        feedback_reply="Old reply"
    )

    response = client.post("/staff_feedback_message_reply/", {
        "id": feedback.id,
        "reply": ""
    })

    feedback.refresh_from_db()
    assert response.status_code == 200
    assert response.content == b"True"
    assert feedback.feedback_reply == ""


# ✅ Test case 5: Gửi ID là chuỗi không hợp lệ
@pytest.mark.django_db
def test_staff_feedback_reply_invalid_id_type(client):
    """
    Test case 5: Gửi phản hồi với ID là chuỗi không hợp lệ.
    Mong đợi: status_code = 200, content = "False".
    """
    response = client.post("/staff_feedback_message_reply/", {
        "id": "abc",
        "reply": "Something"
    })

    assert response.status_code == 200
    assert response.content == b"False"


# ✅ Test case 6: Gửi phản hồi bằng phương thức GET
@pytest.mark.django_db
def test_staff_feedback_reply_get_method(client):
    """
    Test case 6: Gửi phản hồi bằng GET (không hợp lệ).
    Mong đợi: status_code = 200, content = "False".
    """
    response = client.get("/staff_feedback_message_reply/")
    assert response.status_code == 200
    assert response.content == b"False"


# 2 fail, 4 pass


