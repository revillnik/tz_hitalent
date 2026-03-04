import json

from django.test import TestCase
from django.urls import reverse

from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer
from .utils import get_children_departments_with_depth



class DepartmentViewTests(TestCase):
    def test_post_create_department(self) -> None:
        
        url = reverse('departments')

        # проверяем без параметра parent_id
        response = self.client.post(url, data=json.dumps({'name': 'test_department_1'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Department.objects.all().count(), 1)
        self.assertEqual(Department.objects.last().name, 'test_department_1')

        # если parent_id = null
        response = self.client.post(url, data=json.dumps({'name': 'test_department_2', 'parent_id': None}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Department.objects.all().count(), 2)
        self.assertEqual(Department.objects.last().name, 'test_department_2')

        last_department = Department.objects.last()

        # parent_id просто указан правильно
        response = self.client.post(url, data=json.dumps({'name': 'test_department_3', 'parent_id': last_department.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Department.objects.all().count(), 3)
        self.assertEqual(Department.objects.last().name, 'test_department_3')

        # если name одинаковые с name у родителя
        response = self.client.post(url, data=json.dumps({'name': last_department.name, 'parent_id': last_department.id}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

        last_department = Department.objects.last()

        # если id и parent_id одинаковые
        response = self.client.post(url, data=json.dumps({'name': last_department.name, 'parent_id': last_department.parent_id.id}), content_type='application/json')
        self.assertEqual(response.status_code, 400)


        # parent_id не существует (берем последний и +1 ставим)
        response = self.client.post(url, data=json.dumps({'name': 'test_department_1', 'parent_id': last_department.id + 1}), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class DepartmentIdEmployeesViewTests(TestCase):
    def test_post_create_employee_in_department(self) -> None:
        # создаем департамент, чтобы в нем далее создать работников
        created_department = Department.objects.create(name='test_department')
        url = reverse('departments_id_employees', kwargs={'id': created_department.id})
        
        # создаем работника без hired_at
        response = self.client.post(
            url,
            data=json.dumps({'full_name': 'Nikita_1', 'position': 'developer'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.first().full_name, 'Nikita_1')

        # создаем работника с hired_at == null
        response = self.client.post(
            url,
            data=json.dumps({'full_name': 'Nikita_2', 'position': 'developer', 'hired_at':None}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Employee.objects.count(), 2)
        self.assertEqual(Employee.objects.last().full_name, 'Nikita_2')

        # создаем работника c hired_at
        response = self.client.post(
            url,
            data=json.dumps({'full_name': 'Nikita_3', 'position': 'developer', 'hired_at':'2023-01-15'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Employee.objects.count(), 3)
        self.assertEqual(Employee.objects.last().full_name, 'Nikita_3')


class DepartmentIdViewTests(TestCase):
    def test_get_id_department(self):
        # создаем тестовые данные в таблицах
        Department.objects.create(name='test_department')
        Employee.objects.create(full_name='Nikita', position='developer', department_id = Department.objects.last())
        Department.objects.create(name='test_department_1', parent_id = Department.objects.first())
        Department.objects.create(name='test_department_2', parent_id = Department.objects.first())
        Department.objects.create(name='test_department_2_1', parent_id = Department.objects.last())
        Department.objects.create(name='test_department_2_1_1', parent_id = Department.objects.last())

        # проверяем получение департамента и его работников при отсутствии параметров depth и include_employees
        url = reverse('departments_id', kwargs={'id': Department.objects.first().id})
        response = self.client.get(url)
        self.assertEqual(response.json().get('department'), DepartmentSerializer(Department.objects.first()).data)
        self.assertEqual(response.json().get('employees'), EmployeeSerializer(Department.objects.first().department, many=True).data)
        self.assertEqual(response.json().get('children'), get_children_departments_with_depth(department=Department.objects.first(), depth=1))
        
        # проверяем получение департамента и его работников при наличии параметров depth и include_employees
        url = reverse('departments_id', kwargs={'id': Department.objects.first().id})
        response = self.client.get(url, data={'depth': 5, 'include_employees': 'false'})
        self.assertEqual(response.json().get('department'), DepartmentSerializer(Department.objects.first()).data)
        self.assertEqual(response.json().get('employees'), [])
        self.assertEqual(response.json().get('children'), get_children_departments_with_depth(department=Department.objects.first(), depth=5))

    def test_patch_id_department(self):
        Department.objects.create(name='test_department')
        Department.objects.create(name='test_department_1', parent_id = Department.objects.last())
        Department.objects.create(name='test_department_2', parent_id = Department.objects.last())

        url = reverse('departments_id', kwargs={'id': Department.objects.last().id})
        
        # проверяем изменение только name у департамента
        response = self.client.patch(url, data=json.dumps({'name':'udp_test_department'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('name'), 'udp_test_department')
        self.assertEqual(Department.objects.last().name, 'udp_test_department')

        # проверяем изменение только parent_id у департамента на тот, что и у самого департамента
        response = self.client.patch(url, data=json.dumps({'parent_id': Department.objects.last().id}), content_type='application/json')
        self.assertEqual(response.status_code, 409)

        # проверяем изменение только parent_id у департамента на тот, что и образует цикл
        url = reverse('departments_id', kwargs={'id': Department.objects.first().id})
        response = self.client.patch(url, data=json.dumps({'parent_id': Department.objects.last().id}), content_type='application/json')
        self.assertEqual(response.status_code, 409)

        # проверяем изменение только parent_id у департамента
        url = reverse('departments_id', kwargs={'id': Department.objects.last().id})
        response = self.client.patch(url, data=json.dumps({'parent_id': Department.objects.first().id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('parent_id'), Department.objects.first().id)
        self.assertEqual(Department.objects.last().parent_id.id, Department.objects.first().id)

    def test_delete_id_department(self):
        Department.objects.create(name='test_department')
        Department.objects.create(name='test_department_1', parent_id = Department.objects.first())
        Department.objects.create(name='test_department_2', parent_id = Department.objects.first())
        Department.objects.create(name='test_department_2_1', parent_id = Department.objects.last())
        Department.objects.create(name='test_department_2_1_1', parent_id = Department.objects.last())
        Employee.objects.create(full_name='Nikita_1', position='developer', department_id = Department.objects.last())
        Employee.objects.create(full_name='Nikita_2', position='developer', department_id = Department.objects.last())

        # проверяем возникновение ошибки при передаче только параметра mode=reassign
        url = reverse('departments_id', kwargs={'id': Department.objects.first().id})
        response = self.client.delete(url, QUERY_STRING='mode=reassign')
        self.assertEqual(response.status_code, 400)

        # проверяем удаление департамента с переносом работников на другой
        url = reverse('departments_id', kwargs={'id': Department.objects.last().id})
        response = self.client.delete(url, QUERY_STRING=f'mode=reassign&reassign_to_department_id={Department.objects.first().id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Department.objects.last().department.all().exists())
        self.assertEqual(EmployeeSerializer(Department.objects.first().department.all(), many=True).data, EmployeeSerializer(Employee.objects.filter(department_id=Department.objects.first().id), many=True).data)

        # проверяем каскадное удаление департамента и его работников
        url = reverse('departments_id', kwargs={'id': Department.objects.first().id})
        response = self.client.delete(url, QUERY_STRING='mode=cascade')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Department.objects.all().exists())
        self.assertFalse(Employee.objects.all().exists())