from typing import Any

from .models import Department



def validate_depth_parameter(depth: Any) -> bool:
    """
    Функция для валидации параметр depth, который передается в GET запросе по пути /departments/{id}
    """
    
    try:
        depth = int(depth)
        if 0 < depth < 6:
            return True
        return False
    except:
        return False
    

def validate_include_employees_parameter(include_employees: Any) -> bool:
    """
    Функция для валидации параметра include_employees, который передается в GET запросе по пути /departments/{id}
    """

    if include_employees and type(include_employees) == str and include_employees.lower() in ['true', 'false']:
        return True
    else:
        return False
        

def validate_id_parameter(id: Any) -> bool:
    """
    Функция для валидации параметра id, который передается в DELETE запросе по пути /departments/{id}
    """

    try:
        int(id)
        return True
    except:
        return False
    

def validate_mode_parameter(mode: Any) -> bool:
    """
    Функция для валидации параметра mode, который передается в DELETE запросе по пути /departments/{id}
    """

    if mode and type(mode) == str and mode in ['cascade', 'reassign']:
        return True
    else:
        return False
    
    
def validate_department_inheritance_cycle(child_department: Department, list_child_deparment_ids: list = None, parent_id: int = None) -> tuple[list, bool]:
    """
    Функция для рекурсивной проверки наличия цикла в цепочке наследования депортаментов. Применяется в PATCH запросе по пути /departments/{id}
    """
    
    # инициализируем список, добавляем в него parent_id - самой первой итерации
    if list_child_deparment_ids is None:
        list_child_deparment_ids = [parent_id]

    # если цикл есть, то значит в списке наследования будет повторение id депортаментов, 
    # увидеть это мы можем посредством сравнения количества уникальных id и общего количества id
    check_cycle = len(set(list_child_deparment_ids)) == len(list_child_deparment_ids)

    if child_department and check_cycle:
        list_child_deparment_ids.append(child_department.id)
        
        new_check_cycle = len(set(list_child_deparment_ids)) == len(list_child_deparment_ids)

        # если у данного депортамента есть родитель - возвращаем его
        if child_department.parent_id:
            return validate_department_inheritance_cycle(child_department=child_department.parent_id, list_child_deparment_ids=list_child_deparment_ids)
        else:
            return new_check_cycle, list_child_deparment_ids
    else:
        return check_cycle, list_child_deparment_ids

