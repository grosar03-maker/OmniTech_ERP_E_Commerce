import pytest
from django.template import Context, Template


@pytest.mark.django_db
class TestTemplateTags:
    def test_clp_currency_with_value(self):
        t = Template('{% load omnitech_extras %}{{ value|clp_currency }}')
        result = t.render(Context({'value': 1234567}))
        assert result == '1.234.567'

    def test_clp_currency_with_none(self):
        t = Template('{% load omnitech_extras %}{{ value|clp_currency }}')
        result = t.render(Context({'value': None}))
        assert result == '0'

    def test_clp_currency_with_invalid(self):
        t = Template('{% load omnitech_extras %}{{ value|clp_currency }}')
        result = t.render(Context({'value': 'not-a-number'}))
        assert result == '0'

    def test_clp_price_with_value(self):
        t = Template('{% load omnitech_extras %}{{ value|clp_price }}')
        result = t.render(Context({'value': 50000}))
        assert result == '$50.000'

    def test_class_name_with_value(self):
        t = Template('{% load omnitech_extras %}{{ value|class_name }}')
        result = t.render(Context({'value': 'hello'}))
        assert result == 'str'

    def test_class_name_with_none(self):
        t = Template('{% load omnitech_extras %}{{ value|class_name }}')
        result = t.render(Context({'value': None}))
        assert result == ''
