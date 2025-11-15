from datetime import datetime, timedelta

from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL


def test_booking_conflict_detection(app):
    with app.app_context():
        resource = ResourceDAL.get_featured_resources(limit=1)[0]
        student = UserDAL.get_user_by_email('student@campus.test')
        start = datetime.utcnow().replace(microsecond=0)
        end = start + timedelta(hours=2)
        BookingDAL.create_booking(resource.resource_id, student.user_id, start.isoformat(), end.isoformat(), notes=None, status='approved')
        assert BookingDAL.has_conflict(resource.resource_id, (start + timedelta(minutes=30)).isoformat(), (end + timedelta(hours=1)).isoformat())


def test_booking_request_flow(client, app):
    with app.app_context():
        resource = ResourceDAL.get_featured_resources(limit=1)[0]
    login_resp = client.post('/auth/login', data={'email': 'student@campus.test', 'password': 'StudentPass1!'}, follow_redirects=True)
    assert login_resp.status_code == 200
    start = (datetime.utcnow() + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    resp = client.post(f'/bookings/request/{resource.resource_id}', data={
        'start_datetime': start.isoformat(timespec='minutes'),
        'end_datetime': end.isoformat(timespec='minutes'),
        'notes': 'Test booking'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Booking submitted' in resp.data
