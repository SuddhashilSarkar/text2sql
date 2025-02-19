import factory
import factory.fuzzy
import csv
from datetime import date
from faker import Faker

fake = Faker()  # Create Faker instance outside the factory

class StudentFactory(factory.Factory):
    class Meta:
        model = dict

    name = factory.Faker('name')
    age = factory.fuzzy.FuzzyInteger(6, 20)
    gender = factory.fuzzy.FuzzyChoice(['Male', 'Female', 'Other'])
    grade = factory.Faker('random_element', elements=['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th'])
    email = factory.LazyAttribute(lambda _: fake.unique.email())  
    phone = factory.LazyAttribute(lambda _: fake.numerify("##########"))  # 10-digit number format
    address = factory.LazyAttribute(lambda _: fake.address().replace("\n", ", "))  # Remove newlines
    cgpa = factory.fuzzy.FuzzyDecimal(0.0, 10.0)
    enrollment_year = factory.fuzzy.FuzzyInteger(date.today().year - 5, date.today().year)


def generate_fake_data(num_records=100, filename="student_data.csv"):
    data = [StudentFactory() for _ in range(num_records)]

    if not data:
        print("No data generated.")
        return

    fieldnames = data[0].keys()  

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Generated {num_records} records and saved to {filename}")


if __name__ == "__main__":
    generate_fake_data()
