.DEFAULT_GOAL := help

# Универсальный обработчик позиционных аргументов
define handle_args
	$(eval TARGET := $(word 1,$(MAKECMDGOALS)))
	$(eval ARG1 := $(word 2,$(MAKECMDGOALS)))
	$(eval ARG2 := $(word 3,$(MAKECMDGOALS)))
	$(eval ARG3 := $(word 4,$(MAKECMDGOALS)))
endef

run:
	uv run python ./main.py

close:
	kill -9 $(lsof -t -i :8000)

install: ## Установить зависимость с помощью uv
	$(call handle_args)
	@if [ -z "$(LIBRARY)$(ARG1)" ]; then \
		echo "Ошибка: не указано имя библиотеки. Используйте 'make install LIBRARY=имя' или 'make install имя'"; \
		exit 1; \
	fi; \
	LIBRARY=$${LIBRARY:-$(ARG1)}; \
	echo "Установка зависимости $$LIBRARY"; \
	uv add $$LIBRARY

uninstall: ## Удалить зависимость с помощью uv
	$(call handle_args)
	@if [ -z "$(LIBRARY)$(ARG1)" ]; then \
		echo "Ошибка: не указано имя библиотеки. Используйте 'make uninstall LIBRARY=имя' или 'make uninstall имя'"; \
		exit 1; \
	fi; \
	LIBRARY=$${LIBRARY:-$(ARG1)}; \
	echo "Удаление зависимости $$LIBRARY"; \
	uv remove $$LIBRARY

migrate-create: ## Создать новую миграцию
	$(call handle_args)
	@if [ -z "$(MIGRATION)$(ARG1)" ]; then \
		echo "Ошибка: не указано имя миграции. Используйте 'make migrate-create MIGRATION=имя' или 'make migrate-create имя'"; \
		exit 1; \
	fi; \
	MIGRATION=$${MIGRATION:-$(ARG1)}; \
	echo "Создание миграции $$MIGRATION"; \
	alembic revision --autogenerate -m "$$MIGRATION"

migrate-apply: ## Применить миграцию
	alembic upgrade head

help: ## Показать это сообщение о помощи
	@echo "Использование: make [команда] [аргумент]"
	@echo ""
	@echo "Команды:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Позволяет использовать make <target> <arg>
%::
	@: