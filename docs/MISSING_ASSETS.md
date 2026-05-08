# MISSING_ASSETS

Tệp này liệt kê asset còn thiếu sau đợt nâng cấp runtime. Các mục dưới đây đều đã có hook trong code hoặc là nhu cầu trực tiếp để hoàn thiện vertical slice.

## 1. Danh sách thiếu chi tiết

| Asset thiếu | Thiếu ở đâu | Dùng để làm gì | Kích thước gợi ý | Format gợi ý | Naming convention | Priority |
|---|---|---|---|---|---|---|
| `space_loop.wav` | `assets/sounds/ambient/` | Ambient loop cho không gian (`AudioManager.play_ambient`) | 44.1kHz, stereo, 30-90s loopable | `.wav` | `space_loop.wav` | P0 |
| `jetpack.wav` | `assets/sounds/fx/` | SFX thrust khi player tăng tốc | < 0.5s | `.wav` | `jetpack.wav` | P0 |
| `mining.wav` | `assets/sounds/fx/` | SFX khi mining asteroid | 0.1-0.3s | `.wav` | `mining.wav` | P0 |
| `explosion.wav` | `assets/sounds/fx/` | SFX khi asteroid vỡ | 0.2-0.6s | `.wav` | `explosion.wav` | P0 |
| `click.wav` | `assets/sounds/fx/` | UI/interaction click (menu, station, crafting, interaction) | 0.05-0.2s | `.wav` | `click.wav` | P0 |
| `warning.wav` | `assets/sounds/fx/` | Cảnh báo low stat/death | 0.2-0.5s | `.wav` | `warning.wav` | P0 |
| `impact.wav` | `assets/sounds/fx/` | Va chạm asteroid-player | 0.1-0.4s | `.wav` | `impact.wav` | P1 |
| `log01.ogg` ... `log23.ogg` | `assets/sounds/logs/` | Voice playback cho narrative logs (đã có metadata audio trong `data/logs/*.json`) | 44.1kHz mono/stereo, 5-20s mỗi log | `.ogg` | `logNN.ogg` (NN = 01..23) | P1 |

## 2. Thiếu nội dung đề xuất (chưa có hook cứng nhưng cần cho chất lượng vertical slice)

| Asset thiếu | Thiếu ở đâu | Dùng để làm gì | Kích thước gợi ý | Format gợi ý | Naming convention | Priority |
|---|---|---|---|---|---|---|
| Ending splash art (3 biến thể) | `assets/images/ui/endings/` | Hiển thị ending tốt hơn thay vì chỉ text | 1280x720 | `.png` | `ending_good.png`, `ending_neutral.png`, `ending_bad.png` | P2 |
| Station backdrop panel | `assets/images/ui/station/` | Làm station scene đậm chất atmospheric hơn | ~1024x576 | `.png` | `station_panel.png` | P2 |

## 3. Ghi chú triển khai
- Runtime hiện tại vẫn chạy ổn khi thiếu các asset trên nhờ fallback silent/placeholder.
- Để đạt trải nghiệm vertical slice đúng nghĩa, nhóm `P0` nên được bổ sung trước.
- Sau khi drop asset mới, không cần đổi code path nếu giữ đúng naming convention ở bảng trên.
