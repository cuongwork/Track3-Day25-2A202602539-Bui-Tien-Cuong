# Nguồn dữ liệu cho REPORT.md

Các JSON/CSV và biểu đồ trong thư mục này được sinh bằng chương trình của lab.
Đây là dữ liệu mô phỏng, không phải dữ liệu production hoặc ảnh chụp màn hình.
REPORT.md đã được điền từ REPORT_TEMPLATE.md theo yêu cầu. Họ tên/MSV lấy từ tên
thư mục; dòng Commit ghi hash của commit hoàn tất bài ngay trước commit cập nhật dòng này.

| Mục template | File nguồn |
|---|---|
| 1, 2, 7: Game Day và cấu hình | `gameday/naive.json`, `gameday/resilient.json`, `../configs/gameday.yaml` |
| 3: Ba thí nghiệm client | `experiments/results.json` và từng JSON riêng |
| 4: Workflow | `workflows.json` |
| 5: Alerting và error budget | `slo.json` |
| 6: Postmortem G2 | `gameday/naive_G2_overload_storm_timeseries.csv`, `gameday/G2_overload_storm.png` |
| 8: Cache | `cache/resilient.json`, `cache/cached.json`, các thí nghiệm `similarity_*`, `ttl_*`, `stale_disabled` |
| Điểm tự động | `scoreboard.json` |
| Bằng chứng chạy | `verification/*.log` |

Các kết quả so sánh và thí nghiệm dùng seed mô phỏng 25. Grader chạy thêm seed 26, 27.
Mỗi JSON thí nghiệm lưu seed, cấu hình, thay đổi kiểm soát và metric trực tiếp từ simulator.
Các cấu hình cố ý không an toàn chỉ nằm trong script thí nghiệm, không sửa client nộp bài.
Log phản ánh output thật của lệnh chạy; thời gian thực thi và runtime có thể thay đổi khi chạy lại.

Chạy từ thư mục gốc repo bằng Python trong môi trường đã cài `.[dev,plot]`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_gameday.py --client both
.\.venv\Scripts\python.exe scripts/run_workflows.py --executor both
.\.venv\Scripts\python.exe scripts/run_slo.py --alerter both
.\.venv\Scripts\python.exe scripts/run_gameday.py --scenarios configs/scenarios_cache.yaml --client resilient,cached --out reports/cache
.\.venv\Scripts\python.exe scripts/run_report_experiments.py
.\.venv\Scripts\python.exe scripts/plot_timeseries.py --scenario G2_overload_storm
.\.venv\Scripts\python.exe scripts/grade.py --seeds 25,26,27
```

Grader công khai tối đa xác minh được 84/88 điểm tự động: 4 điểm SLO ẩn do giảng viên chấm.
12 điểm report/postmortem được chấm tay. Pass băng công khai không bảo đảm kết quả băng ẩn.
`verification/manifest.json` lưu SHA-256 của nguồn code, cấu hình và artifact tại thời điểm hoàn tất.
