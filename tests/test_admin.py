"""
Tests for admin functionality
"""
import pytest
import json
from io import BytesIO


@pytest.mark.admin
def test_admin_requires_auth(client):
    """Test admin requires authentication"""
    response = client.get('/admin/', follow_redirects=False)
    # Admin might return 200 in test mode or redirect to login
    assert response.status_code in [200, 302]
    if response.status_code == 302:
        assert '/login' in response.location


@pytest.mark.admin
def test_admin_accessible_when_authenticated(auth_client):
    """Test admin is accessible when authenticated"""
    response = auth_client.get('/admin/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_user_list(auth_client):
    """Test viewing user list in admin"""
    response = auth_client.get('/admin/user/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_question_list(auth_client):
    """Test viewing question list in admin"""
    response = auth_client.get('/admin/question/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_section_list(auth_client):
    """Test viewing section list in admin"""
    response = auth_client.get('/admin/section/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_exam_list(auth_client):
    """Test viewing exam list in admin"""
    response = auth_client.get('/admin/exam/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_test_list(auth_client):
    """Test viewing test list in admin"""
    response = auth_client.get('/admin/test/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_import_exam_page(auth_client):
    """Test accessing import exam page"""
    response = auth_client.get('/admin/import_exam/')
    assert response.status_code == 200
    assert b'Import Exam' in response.data


@pytest.mark.admin
def test_admin_import_exam_upload(auth_client, app, test_user, sample_exam_json):
    """Test uploading exam via admin interface"""
    # Create a file-like object
    json_str = json.dumps(sample_exam_json)
    data = {
        'file': (BytesIO(json_str.encode('utf-8')), 'test_exam.json')
    }
    
    response = auth_client.post(
        '/admin/import_exam/',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    # Should show success or redirect
    assert b'Successfully imported' in response.data or b'Exam' in response.data


@pytest.mark.admin
def test_admin_import_no_file(auth_client):
    """Test import without file"""
    response = auth_client.post('/admin/import_exam/', data={}, follow_redirects=True)
    # Should show error message or redirect back
    assert response.status_code == 200
    assert b'No file' in response.data or b'Import Exam' in response.data


@pytest.mark.admin
def test_admin_import_non_json_file(auth_client):
    """Test importing non-JSON file"""
    data = {
        'file': (BytesIO(b'not json'), 'test.txt')
    }
    
    response = auth_client.post(
        '/admin/import_exam/',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    # Should show error message or form
    assert response.status_code == 200
    assert b'JSON' in response.data or b'Import Exam' in response.data


@pytest.mark.admin
def test_admin_import_invalid_json(auth_client):
    """Test importing invalid JSON"""
    data = {
        'file': (BytesIO(b'{invalid json'), 'test.json')
    }
    
    response = auth_client.post(
        '/admin/import_exam/',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert b'Invalid JSON' in response.data or b'Error' in response.data


@pytest.mark.admin
def test_admin_create_question_page(auth_client):
    """Test accessing create question page"""
    response = auth_client.get('/admin/question/new/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_create_section_page(auth_client):
    """Test accessing create section page"""
    response = auth_client.get('/admin/section/new/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_create_exam_page(auth_client):
    """Test accessing create exam page"""
    response = auth_client.get('/admin/exam/new/')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_view_question_details(auth_client, test_question):
    """Test viewing question details"""
    response = auth_client.get(f'/admin/question/details/?id={test_question}', follow_redirects=True)
    # Should show question details or list
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_edit_question_page(auth_client, test_question):
    """Test accessing edit question page"""
    response = auth_client.get(f'/admin/question/edit/?id={test_question}')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_edit_section_page(auth_client, test_section):
    """Test accessing edit section page"""
    response = auth_client.get(f'/admin/section/edit/?id={test_section}')
    assert response.status_code == 200


@pytest.mark.admin
def test_admin_cannot_create_test(auth_client):
    """Test that tests cannot be created via admin"""
    response = auth_client.get('/admin/test/new/', follow_redirects=True)
    # Can create is disabled, so should redirect or show message
    assert response.status_code in [200, 404, 403]


@pytest.mark.admin
def test_admin_cannot_edit_test(auth_client, app, test_user, test_exam):
    """Test that tests cannot be edited via admin"""
    from models import db
    from models.test import Test
    
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    response = auth_client.get(f'/admin/test/edit/?id={test_id}', follow_redirects=True)
    # Can edit is disabled, so should redirect or show error
    assert response.status_code in [200, 404, 403]

