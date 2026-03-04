from .models import Department
from .serializers import DepartmentSerializer



def get_children_departments_with_depth(department: Department, depth: int, depth_counter: int = 0, result_list = None) -> list:
    """
    Функция для рекурсивного получения всех дочерних департаментов с учетом указанного параметра depth (глубина)
    """
    
    # инициируем результирующий список, где сразу создаем словари по каждому уровню
    if result_list is None:
        result_list = [{f'level_{i+1}': list()} for i in range(depth)]

    # как только доходим до последнего уровня - возвращаем результиующий список
    if depth_counter >= depth:
        return result_list
    else:
        # получаем все дочерние депортаменты
        list_department_children = Department.objects.filter(parent_id = department.id)

        if list_department_children:
            # добавляем найденные дочерние депортаменты в результирующий список на тот уровень, где они располагаются
            result_list[depth_counter][f"level_{depth_counter + 1}"].extend(DepartmentSerializer(list_department_children, many=True).data)

            # для каждого дочернего депортамента запускаем рекурсивный обход
            for child_department in list_department_children:
                result_list = get_children_departments_with_depth(
                    department=child_department,
                    depth=depth,
                    result_list=result_list,
                    depth_counter=depth_counter + 1
                    )

    return result_list