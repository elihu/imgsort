PKG=imgsort-1.0-py3-none-any.whl
DEPS=typer
APP_PATH=~/.local/share/imgsort
APP_DIST=$(APP_PATH)/dist

prepare:
	mkdir -p $(APP_PATH)
	mkdir -p $(APP_DIST)

build: prepare
	poetry build
	mv -f dist/$(PKG) $(APP_DIST)/$(PKG)

install: build
	pip3 install $(APP_DIST)/$(PKG)
	rm -rf $(APP_DIST)

clean:
	rm -rf __pycache__
	rm -rf $(APP_PATH)

uninstall: clean
	pip3 uninstall $(APP_DIST)/$(PKG)

