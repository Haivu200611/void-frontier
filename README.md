# Void Frontier

## Mô tả ngắn
Void Frontier là game 2D sinh tồn ngoài không gian, nơi người chơi khám phá khu vực mới, khai thác tài nguyên, quản lý chỉ số sống còn và mở khóa cốt truyện qua các log/terminal.

Dự án được xây dựng bằng **Python** và **pygame**.

## Vòng lặp gameplay
**Khám phá -> Khai thác -> Sinh tồn -> Giải mã -> Mở rộng**

## Tính năng chính
- Di chuyển trong môi trường không trọng lực với quán tính.
- Khai thác asteroid để thu thập tài nguyên.
- Quản lý 5 chỉ số sinh tồn: oxygen, temperature, battery, hunger, pressure.
- Tương tác log/terminal để mở khóa tiến trình cốt truyện.
- Chế tạo module, nâng cấp suit và vật phẩm tiêu hao.
- Mở khóa dần các zone theo tiến độ khám phá.

## Bộ nguyên lý gameplay (đã áp dụng)
- **Core loop rõ ràng**: `Khám phá -> Khai thác -> Sinh tồn -> Giải mã -> Mở rộng`.
- **Risk/Reward**: vào zone sâu sẽ có tài nguyên tốt hơn nhưng hazard mạnh hơn.
- **Tiến trình có khóa mở**: log và terminal mở khóa zone + endgame.
- **Nhiều hướng build**: module căn cứ + nâng cấp suit theo phong cách chơi.
- **Phản hồi trực quan**: HUD hiển thị stat, cảnh báo low stat, mission progress.
- **Fail state và Win state**:
  - Thua khi oxygen/temperature/pressure về 0.
  - Thắng khi mở đủ log + terminal và chọn ending.

## Điều khiển
- `SPACE` (menu): bắt đầu game.
- `W A S D`: di chuyển.
- `SHIFT` hoặc `SPACE` (in-game): phanh.
- Chuột trái: khai thác asteroid.
- `E`: tương tác log/terminal.
- `TAB`: mở giao diện chế tạo.
- `I`: bật/tắt inventory.
- `UP/DOWN`: di chuyển lựa chọn trong menu chế tạo.
- `ENTER`: chế tạo item đang chọn.
- `ESC`: đóng màn hình overlay.
- `1/2/3`: chọn kết thúc khi đủ điều kiện endgame.

## Cài đặt dự án
Cài dependency:

```bash
pip install pygame
```

## Biên dịch và chạy dự án
Chạy ở chế độ phát triển:

```bash
python main.py
```

## Cấu trúc dự án
- `main.py`: vòng lặp game chính.
- `scenes/`: quản lý scene (menu, gameplay, crafting, station).
- `entities/`: thực thể trong game (player, asteroid, hazard, module).
- `systems/`: hệ thống gameplay (world, survival, inventory, crafting, narrative).
- `ui/`: HUD và giao diện phụ.
- `data/`: dữ liệu tĩnh (asteroids, recipes, logs).
- `assets/`: font, hình ảnh và âm thanh.

## Chuẩn asset bắt buộc cho gameplay
- `player`: `player_idle`, `player_move`, `player_thruster`.
- `asteroids`: `iron`, `titanium`, `silicon`, `copper`, `ice`, `carbon`.
- `modules`: `habitat`, `lab`, `greenhouse`, `hangar`, `signal_tower`.
- `ui_hud`: `bar_bg.png`, `bar_fill.png`.
- `ui_icons`: `battery`, `iron`, `titanium`, `silicon`, `copper`, `ice`, `carbon`.

Game sẽ tự kiểm tra các asset core lúc khởi chạy. Nếu thiếu file, game vẫn chạy bằng placeholder để không làm gián đoạn dev, đồng thời in danh sách file thiếu để bổ sung sau.

## Ghi chú
- Nhiều file trong `assets/` đang là placeholder (`Add.md`), phù hợp cho giai đoạn phát triển bài tập nhóm.
- Hiện tại nếu thiếu texture `module_hangar` và `module_signal_tower`, game vẫn hoạt động nhưng sẽ dùng ảnh fallback.
