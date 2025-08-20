#!/usr/bin/env python
"""
Script test đơn giản các Django models
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from blog.models import Person, Musician, Album, Student
from datetime import date

print("🚀 Testing Django Models...")

# Test Person
person = Person.objects.create(first_name="Test", last_name="User")
print(f"✓ Person created: {person}")

# Test Musician & Album
musician = Musician.objects.create(first_name="John", last_name="Doe", instrument="Piano")
album = Album.objects.create(artist=musician, name="Test Album", release_date=date.today(), num_stars=4)
print(f"✓ Musician: {musician}")
print(f"✓ Album: {album}")

# Test Student
student = Student.objects.create(name="Test Student", year_in_school=Student.YearInSchool.FRESHMAN)
print(f"✓ Student: {student} - {student.get_year_in_school_display()}")

print(f"\n📊 Counts:")
print(f"  Persons: {Person.objects.count()}")
print(f"  Musicians: {Musician.objects.count()}")
print(f"  Albums: {Album.objects.count()}")
print(f"  Students: {Student.objects.count()}")

print("\n✅ Test completed successfully!")
