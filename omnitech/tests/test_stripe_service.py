from decimal import Decimal

import pytest


@pytest.mark.django_db
class TestCrearCheckoutSession:
    def test_crear_checkout_session_fisico(self, settings, order, monkeypatch):
        settings.STRIPE_CURRENCY = 'clp'
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            url = 'https://checkout.stripe.com/test'

            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        fake_session = FakeSession(
            id='cs_test_123',
            url='https://checkout.stripe.com/test',
            payment_status='unpaid',
        )

        def fake_create(**kw):
            return fake_session

        monkeypatch.setattr(stripe.checkout.Session, 'create', fake_create)
        from omnitech.stripe_service import crear_checkout_session

        items = [{'nombre': 'Notebook Pro', 'tipo': 'fisico', 'precio': 120000, 'cantidad': 2}]
        session = crear_checkout_session(
            order,
            items,
            'http://testserver/success/',
            'http://testserver/cancel/',
        )
        assert session.url == 'https://checkout.stripe.com/test'

    def test_crear_checkout_session_software(self, settings, order, monkeypatch):
        settings.STRIPE_CURRENCY = 'usd'
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            url = 'https://checkout.stripe.com/test'

        monkeypatch.setattr(stripe.checkout.Session, 'create', lambda **kw: FakeSession())
        from omnitech.stripe_service import crear_checkout_session

        items = [{'nombre': 'Antivirus', 'tipo': 'software', 'precio': 200, 'cantidad': 1}]
        session = crear_checkout_session(
            order,
            items,
            'http://testserver/success/',
            'http://testserver/cancel/',
        )
        assert session.url is not None

    def test_crear_checkout_session_con_envio(self, settings, order, monkeypatch):
        settings.STRIPE_CURRENCY = 'clp'
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            url = 'https://checkout.stripe.com/test'

        monkeypatch.setattr(stripe.checkout.Session, 'create', lambda **kw: FakeSession())
        from omnitech.stripe_service import crear_checkout_session

        order.costo_envio = Decimal('5000')
        items = [{'nombre': 'Monitor', 'tipo': 'fisico', 'precio': 150000, 'cantidad': 1}]
        session = crear_checkout_session(
            order,
            items,
            'http://testserver/success/',
            'http://testserver/cancel/',
        )
        assert session.url is not None


@pytest.mark.django_db
class TestVerificarPago:
    def test_verificar_pago_success(self, settings, monkeypatch):
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            payment_status = 'paid'

        monkeypatch.setattr(stripe.checkout.Session, 'retrieve', lambda id: FakeSession())
        from omnitech.stripe_service import verificar_pago

        assert verificar_pago('cs_test_123') is True

    def test_verificar_pago_unpaid(self, settings, monkeypatch):
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            payment_status = 'unpaid'

        monkeypatch.setattr(stripe.checkout.Session, 'retrieve', lambda id: FakeSession())
        from omnitech.stripe_service import verificar_pago

        assert verificar_pago('cs_test_123') is False

    def test_verificar_pago_exception(self, settings, monkeypatch):
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        def fake_retrieve(id):
            raise Exception('API error')

        monkeypatch.setattr(stripe.checkout.Session, 'retrieve', fake_retrieve)
        from omnitech.stripe_service import verificar_pago

        assert verificar_pago('cs_test_123') is False


@pytest.mark.django_db
class TestObtenerSession:
    def test_obtener_session(self, settings, monkeypatch):
        settings.STRIPE_SECRET_KEY = 'sk_test'
        import stripe

        class FakeSession:
            id = 'cs_test_123'

        monkeypatch.setattr(stripe.checkout.Session, 'retrieve', lambda id: FakeSession())
        from omnitech.stripe_service import obtener_session

        session = obtener_session('cs_test_123')
        assert session.id == 'cs_test_123'
