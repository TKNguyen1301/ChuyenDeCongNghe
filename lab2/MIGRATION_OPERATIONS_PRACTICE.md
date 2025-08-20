# Django Migration Operations - Complete Practice Guide

## Tổng quan về Migration Operations

Migration Operations là các lệnh declarative được sử dụng để:
- Thay đổi cấu trúc database
- Quản lý dữ liệu 
- Thực thi SQL tùy chỉnh
- Chạy code Python trong migration

## Phân loại Operations

### 1. Schema Operations (Thao tác Schema)
- CreateModel, DeleteModel, RenameModel
- AddField, RemoveField, AlterField, RenameField
- AddIndex, RemoveIndex, RenameIndex
- AddConstraint, RemoveConstraint, AlterConstraint
- AlterModelTable, AlterModelOptions, etc.

### 2. Special Operations (Thao tác đặc biệt)
- RunSQL: Thực thi SQL tùy chỉnh
- RunPython: Thực thi code Python
- SeparateDatabaseAndState: Tách logic database và state

## Thực hành chi tiết

### Cấu trúc Migration File
```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('app_name', '0001_initial'),
    ]
    
    operations = [
        # Danh sách các operations
    ]
```

### Các ký hiệu trong makemigrations:
- `+` : Addition (ADDITION)
- `-` : Removal (REMOVAL) 
- `~` : Alteration (ALTERATION)
- `p` : Python (PYTHON)
- `s` : SQL (SQL)
- `?` : Mixed (MIXED)

---

# Django Custom Management Commands - Complete Practice Guide

## Tổng quan về Custom Management Commands

Django Custom Management Commands cho phép bạn tạo các lệnh tùy chỉnh có thể chạy với `python manage.py`. Điều này rất hữu ích cho:

- Tự động hóa các tác vụ quản trị
- Batch processing dữ liệu
- Scheduled tasks (cron jobs)
- Data migration và cleanup
- Administrative utilities

## Cấu trúc thư mục

```
your_app/
    management/
        __init__.py
        commands/
            __init__.py
            your_command.py
            another_command.py
```

## Các loại Commands

### 1. BaseCommand
- Lớp cơ bản cho tất cả management commands
- Phải implement method `handle()`

### 2. AppCommand
- Nhận app labels làm arguments
- Implement `handle_app_config()` thay vì `handle()`

### 3. LabelCommand  
- Nhận arbitrary arguments (labels)
- Implement `handle_label()` thay vì `handle()`

## Thuộc tính quan trọng

- `help`: Mô tả command
- `output_transaction`: Wrap output với BEGIN/COMMIT
- `requires_migrations_checks`: Kiểm tra migrations
- `requires_system_checks`: Kiểm tra system
- `style`: Tạo colored output

## Best Practices

1. **Error Handling**: Sử dụng `CommandError` cho errors
2. **Output**: Dùng `self.stdout` và `self.stderr` thay vì `print`
3. **Arguments**: Sử dụng `add_arguments()` để define parameters
4. **Testing**: Tạo tests cho commands
5. **Documentation**: Viết help text rõ ràng
