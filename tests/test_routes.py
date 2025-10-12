"""
Tests for application routes
"""
import pytest
from models import db
from models.test import Test
from models.test_answer import TestAnswer


@pytest.mark.routes
def test_index_redirect_when_not_authenticated(client):
    """Test index redirects to login when not authenticated"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


@pytest.mark.routes
def test_index_redirect_when_authenticated(auth_client):
    """Test index redirects to exams when authenticated"""
    response = auth_client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/exams' in response.location


@pytest.mark.routes
def test_register_get(client):
    """Test GET request to register page"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data


@pytest.mark.routes
def test_register_post_success(client, app):
    """Test successful user registration"""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data


@pytest.mark.routes
def test_register_post_password_mismatch(client):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'password123',
        'password_confirm': 'different'
    })
    
    assert b'do not match' in response.data


@pytest.mark.routes
def test_register_post_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post('/register', data={
        'email': test_user['email'],
        'password': 'password123',
        'password_confirm': 'password123'
    })
    
    assert b'already registered' in response.data


@pytest.mark.routes
def test_login_get(client):
    """Test GET request to login page"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


@pytest.mark.routes
def test_login_post_success(client, test_user):
    """Test successful login"""
    response = client.post('/login', data={
        'email': test_user['email'],
        'password': test_user['password']
    }, follow_redirects=True)
    
    assert response.status_code == 200


@pytest.mark.routes
def test_login_post_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'email': test_user['email'],
        'password': 'wrongpassword'
    })
    
    assert b'Invalid' in response.data


@pytest.mark.routes
def test_logout(auth_client):
    """Test logout functionality"""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data


@pytest.mark.routes
def test_exams_list_requires_auth(client):
    """Test exams list requires authentication"""
    response = client.get('/exams', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


@pytest.mark.routes
def test_exams_list_authenticated(auth_client, test_exam):
    """Test viewing exams list when authenticated"""
    response = auth_client.get('/exams')
    assert response.status_code == 200
    assert b'Available Exams' in response.data


@pytest.mark.routes
def test_start_exam(auth_client, app, test_user, test_exam):
    """Test starting an exam"""
    response = auth_client.post(
        f'/exam/{test_exam}/start',
        follow_redirects=False
    )
    
    assert response.status_code == 302
    assert '/test/' in response.location


@pytest.mark.routes
def test_start_exam_already_started(auth_client, app, test_user, test_exam):
    """Test starting an exam that's already in progress"""
    # Start exam first time
    response1 = auth_client.post(f'/exam/{test_exam}/start', follow_redirects=True)
    
    # Try to start again
    response2 = auth_client.post(f'/exam/{test_exam}/start', follow_redirects=False)
    
    # Should redirect to existing test
    assert response2.status_code == 302
    assert '/test/' in response2.location


@pytest.mark.routes
def test_take_exam(auth_client, app, test_user, test_exam):
    """Test taking an exam"""
    # Start exam
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    response = auth_client.get(f'/test/{test_id}')
    assert response.status_code == 200
    assert b'Question' in response.data


@pytest.mark.routes
def test_submit_answer(auth_client, app, test_user, test_exam, test_question):
    """Test submitting an answer"""
    # Create test
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    # Submit answer
    response = auth_client.post(f'/test/{test_id}/answer', data={
        'question_id': test_question,
        'selected_answer': 2
    })
    
    assert response.status_code == 200
    assert b'success' in response.data


@pytest.mark.routes
def test_submit_exam(auth_client, app, test_user, test_exam):
    """Test submitting a completed exam"""
    # Create test
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    response = auth_client.post(
        f'/test/{test_id}/submit',
        follow_redirects=False
    )
    
    assert response.status_code == 302
    assert f'/test/{test_id}/results' in response.location


@pytest.mark.routes
def test_test_results(auth_client, app, test_user, test_exam, test_question):
    """Test viewing test results"""
    # Create completed test
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        
        # Add answer
        answer = TestAnswer(
            test_id=test.id,
            user_id=test_user['id'],
            question_id=test_question,
            selected_answer=1
        )
        db.session.add(answer)
        
        # Mark as completed
        from datetime import datetime
        test.completed_at = datetime.utcnow()
        db.session.commit()
        test_id = test.id
    
    response = auth_client.get(f'/test/{test_id}/results')
    assert response.status_code == 200
    assert b'out of' in response.data


@pytest.mark.routes
def test_download_example_json(auth_client):
    """Test downloading example JSON file"""
    response = auth_client.get('/download-example-json')
    assert response.status_code == 200
    assert response.content_type == 'application/json'


@pytest.mark.routes
def test_cannot_access_other_user_test(client, app, test_user, test_admin, test_exam):
    """Test that users cannot access other users' tests"""
    # Create test for test_user
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    # Login as admin
    client.post('/login', data={
        'email': test_admin['email'],
        'password': test_admin['password']
    })
    
    # Try to access test_user's test
    response = client.get(f'/test/{test_id}', follow_redirects=True)
    assert b'do not have permission' in response.data


@pytest.mark.routes
def test_submit_answer_unauthorized(client, app, test_user, test_exam, test_question):
    """Test submitting answer without authentication"""
    with app.app_context():
        test = Test(exam_id=test_exam, user_id=test_user['id'])
        db.session.add(test)
        db.session.commit()
        test_id = test.id
    
    response = client.post(f'/test/{test_id}/answer', data={
        'question_id': test_question,
        'selected_answer': 2
    })
    
    # Should redirect to login
    assert response.status_code == 302

