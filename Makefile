PKG      := imgsort-1.1.0-py3-none-any.whl
APP_PATH := $(HOME)/.local/share/imgsort

.PHONY: help install uninstall dev build clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  dev        Install in editable mode for development"
	@echo "  install    Build wheel and install it system-wide"
	@echo "  uninstall  Remove the installed package"
	@echo "  build      Build the wheel only (output: dist/)"
	@echo "  clean      Remove build artifacts and caches"

dev:
	pip install --editable ".[all]" 2>/dev/null || pip install --editable .

build:
	poetry build

install: build
	mkdir -p $(APP_PATH)
	cp dist/$(PKG) $(APP_PATH)/$(PKG)
	pip3 install $(APP_PATH)/$(PKG)
	rm -f $(APP_PATH)/$(PKG)

uninstall:
	pip3 uninstall -y imgsort

clean:
	rm -rf dist/ build/ __pycache__ imgsort/__pycache__ tools/__pycache__
	rm -rf *.egg-info imgsort/*.egg-info
