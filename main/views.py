from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DepartmentSerializer, EmployeeSerializer
from .models import Department
from .validators import validate_depth_parameter, validate_include_employees_parameter, validate_id_parameter, validate_mode_parameter, validate_department_inheritance_cycle
from .utils import get_children_departments_with_depth



class DepartmentView(APIView):
    """
    Класс представления, реализующий задание:
    1) Создать подразделение
    """
    
    def post(self, request) -> Response:
        """
        Реализация запроса POST для создания подразделения
        """

        department_serializer = DepartmentSerializer(data=request.data)

        if department_serializer.is_valid():
            try:
                department_serializer.save()
                return Response(department_serializer.data, status=200)
            except Exception as error:
                return Response(f'Данные прошли валидацию, но произошла ошибка при сохранении объекта в БД: {error}', status=400)
        else:
            return Response(f'Переданные в POST запросе данные не прошли валидацию: {department_serializer.errors}', status=400)
        

class DepartmentIdEmployeesView(APIView):
    """
    Класс представления, реализующий задание:
    2) Создать сотрудника в подразделении
    """
    
    def post(self, request, *args, **kwargs) -> Response:
        """
        Реализация запроса POST для добавления работника в подразделение
        """

        employee_serializer = EmployeeSerializer(data={**request.data, 'department_id': int(kwargs.get('id'))})

        if employee_serializer.is_valid():
    
            try:
                employee_serializer.save()
                return Response(employee_serializer.data, status=200)
            except Exception as error:
                return Response(f'Данные прошли валидацию, но произошла ошибка при сохранении объекта в БД: {error}', status=400)
        else:
            return Response(f'Переданные в POST запросе данные не прошли валидацию: {employee_serializer.errors}', status=400)


class DepartmentIdView(APIView):
    """
    Класс представления, реализующий задания:
    3) Получить подразделение (детали + сотрудники + поддерево)
    4) Переместить подразделение в другое (изменить parent)
    5) Удалить подразделение

    """
    

    def get(self, request, *args, **kwargs) -> Response:
        """
        Реализация запроса GET для отображения информации о подразделении, его работниках и цепочке наследования
        """

        # получаем id подразделения, переданный в url
        str_id = kwargs.get('id')
        # получаем депортамент, информацию о котором будем выводить
        department = Department.objects.filter(pk=int(str_id)).first()
        
        if department:
            department_serializer = DepartmentSerializer(department)

            # формируем макет словаря для получения информации о депортамент
            result_dict_for_response = {
                'department': department_serializer.data,
                'employees': list(),
                'children': list(),
            }

            # получаем переданные в query GET запроса параметры depth и include_employees и валидируем их
            str_depth = request.GET.get('depth', '1')
            str_include_employees = request.GET.get('include_employees', 'true').lower()
            
            if not(validate_depth_parameter(str_depth)):
                return Response(f'Ошибка валидации параметра depth у GET запроса. Он должен быть числом от 1 до 5. У вас depth={str_depth}', status=400)
            if not(validate_include_employees_parameter(str_include_employees)):
                return Response(f'Ошибка валидации параметра include_employees у GET запроса. Он должен быть булевым значением, у вас include_employees={str_include_employees}', status=400)
            
            # приводим параметры к правильным типам из строк
            depth = int(str_depth)
            include_employees = True if str_include_employees == 'true' else False

            # получаем список работников департамента, сортируем его по полям full_name и created_at, добавляем его в результирующий словарь,
            if include_employees:
                department_employees_orm = department.department.all()
                department_employees_serializer = EmployeeSerializer(department_employees_orm, many=True)
                result_dict_for_response['employees'].extend(department_employees_serializer.data)
                result_dict_for_response['employees'].sort(key=lambda x: (x['full_name'], x['created_at']))

            # вызываем функцию для получения всех дочерних департаментов с учетом параметра depth
            result_dict_for_response['children'] = get_children_departments_with_depth(
                department=department,
                depth=depth
            )
            return Response(result_dict_for_response, status=200)
        
        # если департамента с таким id нет - выводим 404
        else:
            return Response(f'Подразделения с id={str_id} не существует', status=404)
    
    def patch(self, request, *args, **kwargs) -> Response:
        """
        Реализация запроса PATCH для изменения информации о подразделении
        """

        # получаем id подразделения, переданный в url
        str_id = kwargs.get('id')
        id = int(str_id)
        # получаем депортамент, информацию о котором будем изменять
        department = Department.objects.filter(pk=id).first()
        
        if department:
            department_serializer = DepartmentSerializer(data=request.data, instance=department, partial=True)
            
            if department_serializer.is_valid():
                try:
                    # получаем параметр parent_id из сериализованного объекта департамента, если его нет - пропускаем проверку, 
                    # если есть - валидируем на наличие цикла в цепочке наследования
                    if department_serializer.validated_data.get('parent_id'):
                        department_parent_id = department_serializer.validated_data.get('parent_id').id
                        validate_result = validate_department_inheritance_cycle(child_department=Department.objects.get(id=department_parent_id), parent_id=id)

                        if not(validate_result[0]):
                            return Response(f'Такой parent_id нельзя добавить, т.к. образуется цикл зависимостей департаментов. Список наследования id: {validate_result[1]}', status=409)
                    
                    department_serializer.save()
                    return Response(department_serializer.data, status=200)
                except Exception as error:
                    return Response(f'Данные прошли валидацию, но произошла ошибка при сохранении объекта в БД: {error}', status=400)
            else:
                return Response(f'Переданные в PATCH запросе данные не прошли валидацию: {department_serializer.errors}', status=400)
        
        # если департамента с таким id нет - выводим 404
        else:
            return Response(f'Подразделения с id={str_id} не существует', status=404)
        
    def delete(self, request, *args, **kwargs):
        """
        Реализация запроса DELETE для изменения информации о подразделении
        """
        
        # получаем id подразделения, переданный в url
        str_id = kwargs.get('id')
         # получаем депортамент, информацию о котором будем удалять
        department = Department.objects.filter(pk=int(str_id)).first()

        if department:

            # получаем параметр mode, переданный в query DELETE запросе и валидируем его
            str_mode = request.GET.get('mode')
            if not(validate_mode_parameter(str_mode)):
                return Response(f'Ошибка валидации параметра mode у GET запроса. Он должен быть cascade или reassign. У вас mode={str_mode}', status=400)
            
            # приводим к правильному формату параметр
            mode = str_mode.lower()

            # проеряем, если mode - reassign, то должен быть указан и параметр reassign_to_department_id. Также валидируем последний
            str_reassign_to_department_id = request.GET.get('reassign_to_department_id')
            if not(validate_id_parameter(str_reassign_to_department_id)) and str_mode == 'reassign':
                return Response(f'Ошибка валидации параметра reassign_to_department_id у GET запроса. Он должен быть числом. У вас reassign_to_department_id={str_reassign_to_department_id}', status=400)

            # с учетом mode каскадно производим удаление записей из БД
            if mode == 'cascade':
                department.delete()
                return Response(f'Успешно удален департамент {department.name}', status=204)
            # перед удалением записей из БД всех работников департамента переназначаем другому подразделению
            else:
                reassign_to_department_id = int(str_reassign_to_department_id)
                department.department.update(department_id = reassign_to_department_id)
                department.delete()
                return Response(f'Успешно удален департамент {department.name}, а его сотрудники перенесены в подразделение с id={reassign_to_department_id}', status=204)

        else:
            return Response(f'Подразделения с id={str_id} не существует', status=404)

        