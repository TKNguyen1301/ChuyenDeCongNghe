# Test 1: Basic Person Model
from blog.models import Person
p1 = Person.objects.create(first_name="John", last_name="Lennon")
print(f"Created: {p1}")
print(f"All persons: {list(Person.objects.all())}")

# Test 2: Musician-Album Relationship (Many-to-One)
from blog.models import Musician, Album
from datetime import date

musician1 = Musician.objects.create(first_name="John", last_name="Lennon", instrument="Guitar")
album1 = Album.objects.create(artist=musician1, name="Imagine", release_date=date(1971, 9, 9), num_stars=5)
print(f"Album: {album1}, Artist: {album1.artist}")

# Test 3: Student with Choices
from blog.models import Student
student1 = Student.objects.create(name="Alice Smith", year_in_school="SO")
print(f"Student: {student1}, Year: {student1.get_year_in_school_display()}")

# Test 4: Pizza-Toppings (Many-to-Many)
from blog.models import Pizza, Topping
cheese = Topping.objects.create(name="Cheese")
pepperoni = Topping.objects.create(name="Pepperoni")
pizza1 = Pizza.objects.create(name="Margherita")
pizza1.toppings.add(cheese, pepperoni)
print(f"Pizza toppings: {list(pizza1.toppings.all())}")

# Test 5: Many-to-Many with Intermediate Model
from shop.models import Person as ShopPerson, Group, Membership
ringo = ShopPerson.objects.create(name="Ringo Starr")
beatles = Group.objects.create(name="The Beatles")
m1 = Membership.objects.create(person=ringo, group=beatles, date_joined=date(1962, 8, 16), invite_reason="Drummer")
print(f"Beatles members: {list(beatles.members.all())}")

# Test 6: Model Inheritance
from shop.models import Place, Restaurant
restaurant1 = Restaurant.objects.create(name="Joe's Pizza", address="123 Main St", serves_pizza=True)
print(f"Restaurant: {restaurant1}")
print(f"All places: {list(Place.objects.all())}")

# Test 7: Advanced Queries và Field Types Examples
from shop.models import Manufacturer, Car
from datetime import date, datetime, time, timedelta
import uuid

# Basic manufacturer and car
toyota = Manufacturer.objects.create(name="Toyota", country="Japan")
car1 = Car.objects.create(manufacturer=toyota, name="Camry", year=2023)
japanese_cars = Car.objects.filter(manufacturer__country="Japan")
print(f"Japanese cars: {list(japanese_cars)}")

# Test advanced field types
print("\n=== Advanced Field Types Demo ===")

# Test 8: Comprehensive Field Types Model
from blog.models import *
from shop.models import *
