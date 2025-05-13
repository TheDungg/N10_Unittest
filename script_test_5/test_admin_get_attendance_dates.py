import pytest
from django.test import Client
from django.urls import reverse
from student_management_app.models import (
    CustomUser, Courses, Subjects, Students,
    Attendance, AttendanceReport, SessionYearModel,
    FeedbackStudent, LeaveReportStaff
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

# Test case 1
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

# Test case 2
def test_admin_get_attendance_student_invalid_id(setup_data):
    client = setup_data["client"]
    url = reverse("admin_get_attendance_student")
    response = client.post(url, {
        "attendance_date": 9999  # ID không tồn tại
    })
    assert response.status_code == 200 or response.status_code == 500
    assert response.content.decode() == "False"

# Test case 3
def test_get_students_success(setup_data):
    client = setup_data["client"]
    subject = setup_data["subject"]
    session = setup_data["session"]
    url = reverse("get_students")
    response = client.post(url, {
        "subject": subject.id,
        "session_year": session.id
    })
    assert response.status_code == 200
    data = response.json()
    names = [d["name"] for d in data]
    assert "Nguyen Van A" in names
    assert "Tran Thi B" in names

# Test case 4
def test_get_students_invalid_subject(setup_data):
    client = setup_data["client"]
    session = setup_data["session"]
    url = reverse("get_students")
    response = client.post(url, {
        "subject": 9999,
        "session_year": session.id
    })
    assert response.status_code == 500

# Test case 5
def test_student_feedback_creation(setup_data):
    student = Students.objects.get(admin=setup_data["student_user1"])
    feedback = FeedbackStudent.objects.create(
        student_id=student,
        feedback="The system is great!",
        feedback_reply=""
    )
    assert feedback.feedback == "The system is great!"
    assert feedback.feedback_reply == ""

# Test case 6
def test_staff_leave_request(setup_data):
    staff_user = CustomUser.objects.create_user(
        username="staff1", password="staffpass", user_type=2
    )
    staff = staff_user.staffs
    leave = LeaveReportStaff.objects.create(
        staff_id=staff,
        leave_date="2024-04-15",
        leave_message="Sick leave",
        leave_status=0
    )
    assert leave.leave_message == "Sick leave"
    assert leave.leave_status == 0

# Test case 7
def test_admin_get_attendance_dates_success(setup_data):
    client = setup_data["client"]
    subject = setup_data["subject"]
    session = setup_data["session"]
    attendance = setup_data["attendance"]
    url = reverse("admin_get_attendance_dates")
    response = client.post(url, {
        "subject": subject.id,
        "session_year_id": session.id
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == attendance.id
    assert data[0]["session_year_id"] == session.id

# Test case 8
def test_admin_get_attendance_dates_invalid_subject(setup_data):
    client = setup_data["client"]
    session = setup_data["session"]
    url = reverse("admin_get_attendance_dates")
    response = client.post(url, {
        "subject": 9999,
        "session_year_id": session.id
    })
    assert response.status_code == 500
