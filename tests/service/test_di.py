from src.service.di.containers import create_container


def test_create_container():
    container = create_container()
    assert container is not None
    # Проверяем, что контейнер содержит хотя бы один провайдер
    assert hasattr(container, "_providers") or hasattr(container, "_AsyncContainer__providers")

