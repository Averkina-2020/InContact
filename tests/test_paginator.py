import pytest

from django.core.paginator import Paginator, Page


class TestPaginatorView:

    @pytest.mark.django_db(transaction=True)
    def test_index_paginator_view_get(self, client):
        response = client.get(f'/')
        assert response.status_code != 404, 'Страница `/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'paginator' in response.context, \
            'Проверьте, что передали переменную `paginator` в контекст страницы `/`'
        assert type(response.context['paginator']) == Paginator, \
            'Проверьте, что переменная `paginator` на странице `/` типа `Paginator`'
        assert 'page' in response.context, \
            'Проверьте, что передали переменную `page` в контекст страницы `/`'
        assert type(response.context['page']) == Page, \
            'Проверьте, что переменная `page` на странице `/` типа `Page`'
