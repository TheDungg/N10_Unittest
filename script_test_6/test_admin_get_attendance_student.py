import pytest
from django.test import Client
from django.urls import reverse
from student_management_app.models import (
    CustomUser, Courses, Subjects, Students,
    Attendance, AttendanceReport, SessionYearModel
)

@pytest.fixture
def setup_data(db):
    client = Client()

    # Tạo user HOD và đăng nhập
    admin_user = CustomUser.objects.create_user(
        username='admin1',
        password='adminpass',
        user_type=1
    )
    client.login(username='admin1', password='adminpass')

    # Tạo năm học và khóa học
    session = SessionYearModel.objects.create(
        session_start_year='2024-01-01',
        session_end_year='2024-12-31'
    )
    course = Courses.objects.create(course_name="Django Course")

    # Tạo môn học
    subject = Subjects.objects.create(
        subject_name="Unit Testing",
        course_id=course,
        staff_id=admin_user
    )

    # Tạo 2 học sinh
    student_user1 = CustomUser.objects.create_user(
        username='student1',
        password='pass123',
        user_type=3,
        first_name='Nguyen',
        last_name='Van A'
    )
    student1 = Students.objects.get(admin=student_user1)

    student_user2 = CustomUser.objects.create_user(
        username='student2',
        password='pass123',
        user_type=3,
        first_name='Tran',
        last_name='Thi B'
    )
    student2 = Students.objects.get(admin=student_user2)

    # Tạo bản ghi điểm danh
    attendance = Attendance.objects.create(
        subject_id=subject,
        attendance_date='2024-04-10',
        session_year_id=session
    )

    # Tạo báo cáo điểm danh
    AttendanceReport.objects.create(
        student_id=student1,
        attendance_id=attendance,
        status=True
    )
    AttendanceReport.objects.create(
        student_id=student2,
        attendance_id=attendance,
        status=False
    )

    return {
        "client": client,
        "attendance": attendance,
        "student_user1": student_user1,
        "student_user2": student_user2,
        "subject": subject,
        "session": session,
        "course": course,
        "admin_user": admin_user
    }

# Test case 1: Truy xuất danh sách điểm danh theo ID hợp lệ
def test_admin_get_attendance_student_success(setup_data):
    client = setup_data["client"]
    attendance = setup_data["attendance"]
    user1 = setup_data["student_user1"]
    user2 = setup_data["student_user2"]
    url = reverse("admin_get_attendance_student")
    response = client.post(url, {
        "attendance_date": attendance.id
    })
    assert response.status_code == 200
    data = response.json()
    student_a = next((s for s in data if s["id"] == user1.id), None)
    assert student_a is not None
    assert student_a["name"] == "Nguyen Van A"
    assert student_a["status"] is True
    student_b = next((s for s in data if s["id"] == user2.id), None)
    assert student_b["name"] == "Tran Thi B"
    assert student_b["status"] is False

# Test case 2: Truy xuất với ID không tồn tại, kỳ vọng trả về lỗi hoặc chuỗi 'false'
def test_admin_get_attendance_student_invalid_id(setup_data):
    client = setup_data["client"]
    url = reverse("admin_get_attendance_student")
    response = client.post(url, {
        "attendance_date": 9999  # ID không tồn tại
    })
    assert response.status_code == 200 or response.status_code == 500
    assert response.content.decode() == "False"
