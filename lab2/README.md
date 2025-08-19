# Django Models Lab 2

Đây là project demo từng bước theo Django Models Documentation.

## Các Models đã implement:

### 1. Basic Models
- **Person**: Model cơ bản với custom methods và properties
- **Student**: Model với choices, Meta options
- **StudentInherited**: Abstract base class inheritance

### 2. Relationships
- **Manufacturer & Car**: ForeignKey (Many-to-One)
- **Pizza & Topping**: ManyToManyField 
- **Group & Person**: ManyToManyField với through model (Membership)
- **Place & Restaurant**: Model inheritance
- **Waiter**: ForeignKey đến Restaurant

### 3. Advanced Features
- **Blog**: Custom save() method
- Meta options (ordering, verbose_name, db_table)
- Custom model methods và properties
- Field options (choices, null, blank, unique, etc.)

## Các Field Types được sử dụng:
- CharField
- EmailField  
- DateField
- DateTimeField
- PositiveIntegerField
- DecimalField
- BooleanField
- ForeignKey
- ManyToManyField
- OneToOneField (through inheritance)

## Cách chạy:

### 1. Setup:
```bash
cd lab2
source ./venv/bin/activate
python manage.py migrate
```

### 2. Tạo superuser:
```bash
python manage.py createsuperuser
```

### 3. Chạy server:
```bash
python manage.py runserver
```

### 4. Truy cập Admin:
- URL: http://127.0.0.1:8000/admin/
- Login với superuser đã tạo

### 5. Test models:
```bash
python manage.py shell < demo_usage.py
```

## Features từ Django Documentation đã implement:

✅ Quick example (Person model)
✅ Field types (CharField, EmailField, DateField, etc.)
✅ Field options (null, blank, choices, unique, etc.)
✅ Verbose field names
✅ Many-to-one relationships (ForeignKey)
✅ Many-to-many relationships (ManyToManyField)
✅ Extra fields on many-to-many (through model)
✅ One-to-one relationships (inheritance)
✅ Meta options (ordering, verbose_name, db_table)
✅ Model methods (__str__, custom methods, properties)
✅ Overriding predefined model methods (save())
✅ Abstract base classes
✅ Multi-table inheritance

## File Structure:
```
lab2/
├── manage.py
├── demo_usage.py           # Demo script
├── myproject/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/                  # Django app
│   ├── models.py          # Tất cả models
│   ├── admin.py           # Admin configurations
│   ├── migrations/        # Database migrations
│   └── ...
└── venv/                  # Virtual environment
```
