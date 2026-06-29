import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestRegistro:
    def test_registro_get_returns_200(self, client):
        response = client.get(reverse('registro'))
        assert response.status_code == 200

    def test_registro_redirects_authenticated_user(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('registro'))
        assert response.status_code == 302

    def test_registro_missing_fields(self, client):
        response = client.post(reverse('registro'), {'username': '', 'email': '', 'password': ''})
        assert response.status_code == 302

    def test_registro_password_mismatch(self, client):
        response = client.post(reverse('registro'), {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'testpass123', 'password2': 'different',
        })
        assert response.status_code == 302

    def test_registro_password_too_short(self, client):
        response = client.post(reverse('registro'), {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'short', 'password2': 'short',
        })
        assert response.status_code == 302

    def test_registro_duplicate_username(self, client, user):
        response = client.post(reverse('registro'), {
            'username': 'testuser', 'email': 'other@test.com',
            'password': 'testpass123', 'password2': 'testpass123',
        })
        assert response.status_code == 302

    def test_registro_duplicate_email(self, client, user):
        response = client.post(reverse('registro'), {
            'username': 'otheruser', 'email': 'test@example.com',
            'password': 'testpass123', 'password2': 'testpass123',
        })
        assert response.status_code == 302

    def test_registro_success_redirects_home(self, client):
        response = client.post(reverse('registro'), {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'testpass123', 'password2': 'testpass123',
        })
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
class TestLogin:
    def test_login_get_returns_200(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_redirects_authenticated_user(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('login'))
        assert response.status_code == 302

    def test_login_with_username(self, client, user):
        response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        assert response.status_code == 302

    def test_login_with_email(self, client, user):
        response = client.post(reverse('login'), {'username': 'test@example.com', 'password': 'testpass123'})
        assert response.status_code == 302

    def test_login_wrong_password(self, client, user):
        response = client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        response = client.post(reverse('login'), {'username': 'nobody', 'password': 'testpass123'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogout:
    def test_logout_logs_out_user(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('logout'))
        assert response.status_code == 302
        assert '_auth_user_id' not in client.session


@pytest.mark.django_db
class TestPasswordReset:
    def test_password_reset_get_returns_200(self, client):
        response = client.get(reverse('password_reset_request'))
        assert response.status_code == 200

    def test_password_reset_redirects_authenticated(self, client, user):
        client.login(username='testuser', password='testpass123')
        response = client.get(reverse('password_reset_request'))
        assert response.status_code == 302

    def test_password_reset_missing_email(self, client):
        response = client.post(reverse('password_reset_request'), {'email': ''})
        assert response.status_code == 302

    def test_password_reset_with_valid_email(self, client, user, monkeypatch):
        calls = []

        def fake_send(**kwargs):
            calls.append(kwargs)
            return 1

        monkeypatch.setattr('omnitech.views_auth.send_mail', fake_send)
        response = client.post(reverse('password_reset_request'), {'email': 'test@example.com'})
        assert response.status_code == 302
        assert len(calls) == 1

    def test_password_reset_with_username_as_email(self, client, user, monkeypatch):
        calls = []

        def fake_send(**kwargs):
            calls.append(kwargs)
            return 1

        monkeypatch.setattr('omnitech.views_auth.send_mail', fake_send)
        response = client.post(reverse('password_reset_request'), {'email': 'testuser'})
        assert response.status_code == 302
        assert len(calls) == 1

    def test_password_reset_nonexistent_email(self, client, user, monkeypatch):
        calls = []

        def fake_send(**kwargs):
            calls.append(kwargs)
            return 1

        monkeypatch.setattr('omnitech.views_auth.send_mail', fake_send)
        response = client.post(reverse('password_reset_request'), {'email': 'nonexistent@test.com'})
        assert response.status_code == 302
        assert len(calls) == 0


@pytest.mark.django_db
class TestPasswordResetConfirm:
    def test_password_reset_confirm_invalid_link(self, client):
        response = client.get(reverse('password_reset_confirm', args=['bad', 'token']))
        assert response.status_code == 302

    def test_password_reset_confirm_valid_link_get(self, client, user):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = client.get(reverse('password_reset_confirm', args=[uidb64, token]))
        assert response.status_code == 200

    def test_password_reset_confirm_valid_link_post(self, client, user):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = client.post(
            reverse('password_reset_confirm', args=[uidb64, token]),
            {'password': 'newpass123', 'password2': 'newpass123'},
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password('newpass123')

    def test_password_reset_confirm_short_password(self, client, user):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = client.post(
            reverse('password_reset_confirm', args=[uidb64, token]),
            {'password': 'short', 'password2': 'short'},
        )
        assert response.status_code == 200

    def test_password_reset_confirm_password_mismatch(self, client, user):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = client.post(
            reverse('password_reset_confirm', args=[uidb64, token]),
            {'password': 'newpass123', 'password2': 'different'},
        )
        assert response.status_code == 200
