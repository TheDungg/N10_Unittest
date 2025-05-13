import pytest
import json
from django.test import Client
from django.urls import reverse
from student_management_app.models import (
    CustomUser, Courses, Subjects, Students,
    Attendance, AttendanceReport, SessionYearModel,
    FeedbackStudent
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
    client.force_login(admin_user)

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

    # Tạo học sinh
    student_user = CustomUser.objects.create_user(
        username='student1',
        password='pass123',
        user_type=3,
        first_name='Nguyen',
        last_name='Van A'
    )
    student = Students.objects.get(admin=student_user)

    # Tạo bản ghi điểm danh
    attendance = Attendance.objects.create(
        subject_id=subject,
        attendance_date='2024-04-10',
        session_year_id=session
    )

    # Tạo báo cáo điểm danh cho học sinh
    AttendanceReport.objects.create(
        student_id=student,
        attendance_id=attendance,
        status=True
    )

    return {
        "client": client,
        "attendance": attendance,
        "student_user": student_user,
        "subject": subject,
        "session": session,
        "course": course,
        "admin_user": admin_user
    }

# Test Case 1: Kiểm tra lấy ngày điểm danh thành công
def test_case_1_get_attendance_dates_success(setup_data):
    client = setup_data["client"]
    subject = setup_data["subject"]
    session = setup_data["session"]
    attendance = setup_data["attendance"]
    url = reverse("get_attendance_dates")

    response = client.post(url, {
        "subject": subject.id,
        "session_year_id": session.id
    }, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    assert response.status_code == 200
    data = json.loads(response.content)
    assert any(item["id"] == attendance.id for item in data)

# Test Case 2: Kiểm tra tạo phản hồi học sinh
def test_case_2_create_feedback_student():
    session = SessionYearModel.objects.create(
        session_start_year="2024-01-01",
        session_end_year="2024-12-31"
    )
    course = Courses.objects.create(course_name="Django Course")
    subject = Subjects.objects.create(subject_name="Unit Testing", course_id=course)

    student_user = CustomUser.objects.create_user(
        username="student1", password="pass123", user_type=3
    )
    student = Students.objects.get(admin=student_user)
    student.session_year_id = session
    student.course_id = course
    student.save()

    feedback = FeedbackStudent.objects.create(
        student_id=student,
        feedback="Tôi cần cải thiện giao diện",
        feedback_reply=""
    )
    assert feedback.feedback == "Tôi cần cải thiện giao diện"
    assert feedback.feedback_reply == ""

# Test Case 3: Kiểm tra lưu điểm danh thành công
def test_case_3_save_attendance_data_success(setup_data):
    client = setup_data["client"]
    student = Students.objects.get(admin=setup_data["student_user"])
    subject = setup_data["subject"]
    session = setup_data["session"]
    url = reverse("save_attendance_data")

    response = client.post(url, {
        "student_ids": json.dumps([{"id": student.admin.id, "status": True}]),
        "subject_id": subject.id,
        "attendance_date": "2024-04-11",
        "session_year_id": session.id
    })

    assert response.status_code == 200
    assert response.content.decode() == "OK"

# Test Case 4: Lỗi khi lưu điểm danh với subject không tồn tại
def test_case_4_save_attendance_data_invalid_subject(setup_data):
    client = setup_data["client"]
    session = setup_data["session"]
    student = Students.objects.get(admin=setup_data["student_user"])
    url = reverse("save_attendance_data")

    response = client.post(url, {
        "student_ids": json.dumps([{"id": student.admin.id, "status": True}]),
        "subject_id": 9999,
        "attendance_date": "2024-04-11",
        "session_year_id": session.id
    })

    assert response.status_code == 200
    assert response.content.decode() == "Error"

# Test Case 5: Kiểm tra cập nhật điểm danh thành công
def test_case_5_update_attendance_data_success(setup_data):
    client = setup_data["client"]
    attendance = setup_data["attendance"]
    student = Students.objects.get(admin=setup_data["student_user"])
    url = reverse("update_attendance_data")

    response = client.post(url, {
        "student_ids": json.dumps([{"id": student.admin.id, "status": False}]),
        "attendance_date": attendance.id
    })

    assert response.status_code == 200
    assert response.content.decode() == "OK"

    updated_report = AttendanceReport.objects.get(attendance_id=attendance, student_id=student)
    assert updated_report.status is False
