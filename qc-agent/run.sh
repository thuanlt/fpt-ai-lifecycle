SANDBOX=0

if [ $SANDBOX == "1" ]; then
    WORKING_DIR="$(dirname "$(realpath "$0")")"
    cp .env.sandbox .env
    cp config.json.sandbox config.json
else
    WORKING_DIR="$(dirname "$(realpath "$0")")"
    cp .env.host .env
    cp config.json.host config.json
fi

ENV_FILE=".env"

# Kiểm tra xem dòng WORKING_DIR=... đã tồn tại trong file .env chưa
# grep -q: Chế độ yên lặng, không in ra output, chỉ trả về mã thoát
if grep -q "^WORKING_DIR=" "$ENV_FILE"; then
    # Nếu đã tồn tại, thay thế dòng đó bằng lệnh sed
    echo "Đã tìm thấy WORKING_DIR. Đang cập nhật giá trị..."
    # sed -i: Chỉnh sửa tại chỗ (in-place)
    # Dùng | làm dấu phân cách để tránh lỗi nếu $WORKING_DIR chứa dấu /
    sed -i "s|^WORKING_DIR=.*|WORKING_DIR=$WORKING_DIR|" "$ENV_FILE"
else
    # Nếu chưa tồn tại, thêm dòng mới vào cuối file
    echo "Không tìm thấy WORKING_DIR. Đang thêm dòng mới..."
    echo "WORKING_DIR=$WORKING_DIR" >> "$ENV_FILE"
fi

echo "File $ENV_FILE đã được cập nhật thành công."

# RUN IT
if [ $SANDBOX == "1" ]; then
    SANDBOX_SET_UID_GID=1 \
    PYTHONPATH=$PYTHONPATH:./src/ \
    python3 src/utils/sandbox_docker.py
else
    PYTHONPATH=$PYTHONPATH:./src/ \
    python3 src/app_test_cycle.py
    # python3 src/app_test_case.py
fi