import pytest
import json
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

# Test case 1: Lưu dữ liệu điểm danh thành công
def test_save_attendance_data_success(setup_data):
    client = setup_data["client"]
    session = setup_data["session"]
    subject = setup_data["subject"]
    student1 = setup_data["student_user1"]
    student2 = setup_data["student_user2"]

    url = reverse("save_attendance_data")
    student_ids = json.dumps([
        {"id": student1.id, "status": True},
        {"id": student2.id, "status": False}
    ])

    response = client.post(url, {
        "student_ids": student_ids,
        "subject_id": subject.id,
        "attendance_date": "2024-04-11",
        "session_year_id": session.id
    })

    assert response.status_code == 200
    assert response.content.decode() == "OK"

    # Kiểm tra dữ liệu đã lưu
    attendance_records = AttendanceReport.objects.filter(attendance_id__attendance_date="2024-04-11")
    student_names = {r.student_id.admin.first_name: r.status for r in attendance_records}
    assert student_names["Nguyen"] is True
    assert student_names["Tran"] is False

# Test case 2: Gửi dữ liệu lỗi (subject không tồn tại)
def test_save_attendance_data_invalid_subject(setup_data):
    client = setup_data["client"]
    session = setup_data["session"]
    student1 = setup_data["student_user1"]
    url = reverse("save_attendance_data")
    student_ids = json.dumps([
        {"id": student1.id, "status": True}
    ])

    response = client.post(url, {
        "student_ids": student_ids,
        "subject_id": 9999,  # subject không tồn tại
        "attendance_date": "2024-04-11",
        "session_year_id": session.id
    })

    assert response.status_code == 200
    assert response.content.decode() == "Error"
