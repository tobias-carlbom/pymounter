NAME = PyMounter
BUNDLE = PyMounter.app
BUILD_DIR = build
SRC = program.py

ifeq ($(OS),Windows_NT)
	TARGET = $(BUILD_DIR)/$(NAME).exe
	MKDIR = if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"
	CLEAN = if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
else
	TARGET = $(BUILD_DIR)/$(BUNDLE)
	MKDIR = mkdir -p
	CLEAN = rm -rf $(BUILD_DIR)
endif

all: $(TARGET)

$(BUILD_DIR)/$(NAME).exe: $(SRC)
	@$(MKDIR)
	nuitka --standalone --windows-console-mode=attach --output-dir=$(BUILD_DIR) --output-filename=$(NAME).exe $(SRC)

$(BUILD_DIR)/$(BUNDLE): $(SRC)
	nuitka --standalone --output-dir=$(BUILD_DIR) --output-filename=$(NAME) $(SRC)
	@mkdir -p $(BUILD_DIR)/$(BUNDLE)/Contents/MacOS
	@cp -R $(BUILD_DIR)/program.dist/* $(BUILD_DIR)/$(BUNDLE)/Contents/MacOS/
	@echo '<?xml version="1.0" encoding="UTF-8"?>' > $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '<plist version="1.0"><dict>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '  <key>CFBundleExecutable</key><string>$(NAME)</string>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '  <key>CFBundleIdentifier</key><string>com.carlbomsdata.mountshare</string>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '  <key>CFBundlePackageType</key><string>APPL</string>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '  <key>LSBackgroundOnly</key><true/>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist
	@echo '</dict></plist>' >> $(BUILD_DIR)/$(BUNDLE)/Contents/Info.plist

clean:
	$(CLEAN)

.PHONY: all clean