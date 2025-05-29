from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    codigo = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.user.username if self.user else ''} ({self.codigo})"
    
##  Tables crated in the database (postgreSQL)
## Managed =False means that Django will not manage the creation or deletion of these tables.

class Country(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'countries'

class ContractType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)

    class Meta:
        managed = False
        db_table = 'contract_types'

class EmployeeType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)

    class Meta:
        managed = False
        db_table = 'employee_types'

class Department(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    country_code = models.ForeignKey(Country, on_delete=models.DO_NOTHING, db_column='country_code')

    class Meta:
        managed = False
        db_table = 'departments'

class City(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    dept_code = models.ForeignKey(Department, on_delete=models.DO_NOTHING, db_column='dept_code')

    class Meta:
        managed = False
        db_table = 'cities'

class Faculty(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    location = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15)
    dean_id = models.CharField(max_length=15, unique=True, null=True, blank=True)  # FK a Employees.id pero no lo ponemos como FK para evitar problemas circulares

    class Meta:
        managed = False
        db_table = 'faculties'
        
    def get_dean(self):
        from yourapp.models import Employee
        if self.dean_id:
            return Employee.objects.filter(id=self.dean_id).first()
        return None

class Campus(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    city_code = models.ForeignKey(City, on_delete=models.DO_NOTHING, db_column='city_code')

    class Meta:
        managed = False
        db_table = 'campuses'

class Employee(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    contract_type = models.ForeignKey(ContractType, on_delete=models.DO_NOTHING, db_column='contract_type')
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, db_column='employee_type')
    faculty_code = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING, db_column='faculty_code')
    campus_code = models.ForeignKey(Campus, on_delete=models.DO_NOTHING, db_column='campus_code')
    birth_place_code = models.ForeignKey(City, on_delete=models.DO_NOTHING, db_column='birth_place_code')

    class Meta:
        managed = False
        db_table = 'employees'

class Area(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    faculty_code = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING, db_column='faculty_code')
    coordinator_id = models.CharField(max_length=15, unique=True)  # FK a Employees.id, pero lo dejamos como char para evitar relaciones circulares

    class Meta:
        managed = False
        db_table = 'areas'
        
    def get_coordinator(self):
        from .models import Employee
        return Employee.objects.filter(id=self.coordinator_id).first()

class Program(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    area_code = models.ForeignKey(Area, on_delete=models.DO_NOTHING, db_column='area_code')

    class Meta:
        managed = False
        db_table = 'programs'

class Subject(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30)
    program_code = models.ForeignKey(Program, on_delete=models.DO_NOTHING, db_column='program_code')

    class Meta:
        managed = False
        db_table = 'subjects'

class Group(models.Model):
    id = models.AutoField(primary_key=True)  # Django necesita una PK
    number = models.IntegerField()
    semester = models.CharField(max_length=6)
    subject_code = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, db_column='subject_code')
    professor_id = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'groups'
        unique_together = (('number', 'subject_code', 'semester'),)

    def get_professor(self):
        if not hasattr(self, '_cached_professor'):
            from .models import Employee
            self._cached_professor = Employee.objects.filter(id=self.professor_id).first()
        return self._cached_professor

class Enrollment(models.Model):
    id = models.AutoField(primary_key=True)  # Django necesita una PK
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # FK real y directa
    
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed= True
        db_table = 'enrollments'
        unique_together = (('student', 'group'),)
