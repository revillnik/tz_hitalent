from rest_framework import serializers

from .models import Department, Employee



class DepartmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор, который реализует перевод данных из json формата в объект модели Department и обратно в json формат.
    """

    class Meta:
        # связываем сериализатор с моделью Department
        model = Department
        # добавляем все поля модели, которые будут учитываться при сериализации
        fields = '__all__'

    def validate_name(self, value: str) -> str:
        """
        Функция для валидации поля name.
        """

        # проверяем наличие поля name, его тип и не пустое ли оно
        if not(value) or type(value) != str or not value.strip():
            raise serializers.ValidationError('Название подразделения не может быть пустым.')
        
        return value.strip()

    def validate_parent_id(self, value: int) -> int:
        """
        Функция для валидации поля parent_id.
        """

        # проверяем является ли поле parent_id равным id самого себя. Надо учитывать, что данная проверка проходит лишь при изменении объекта модели Department 
        # (т.к. при создании self.instance - None). Это допустимо, т.к. parent_id уже связано через FK и если мы захотим указать несуществующий id в поле parent_id модель сама выдаст ошибку
        if value and self.instance and value == self.instance.pk :
            raise serializers.ValidationError('Подразделение не может быть родителем самого себя.')
        
        return value
    
    def validate(self, attrs):
        """
        Функция для общей валидации полей
        """

        # если нет parent_id, то это допускается
        if attrs.get('parent_id') is None:
            return super().validate(attrs)
        
        # получаем родительский департамент
        parent_department = Department.objects.filter(id=attrs.get('parent_id').id).first()
        # получаем весь список его дочерних департаментов
        list_all_childs_department_from_parent = Department.objects.filter(parent_id = parent_department.id)

        if not(parent_department):
            raise serializers.ValidationError('Подразделение может быть дочерним только для другого существующего подразделения.')
        # если среди дочерних департаментов есть названия такие же, какое мы хотим присвоить (или у родительского такое же), выдаем ошибку
        elif attrs.get('name') in (department.name for department in list_all_childs_department_from_parent) or attrs.get('name') == parent_department.name:
            raise serializers.ValidationError('Подразделение может быть дочерним только для другого существующего подразделения с другим именем, имена дочерних подразделений которого должны различаться. ')
        
        return super().validate(attrs)

    def update(self, instance: Department, validated_data: dict) -> Department:
        """
        Реализуем изменение данных в БД
        """
        
        instance.name = validated_data.get('name', instance.name)
        instance.parent_id = validated_data.get('parent_id', instance.parent_id)
        instance.save()
        return instance

    def create(self, validated_data:dict) -> Department:
        """
        Реализуем сохранение данных в БД
        """

        return Department.objects.create(**validated_data)
    

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Сериализатор, который реализует перевод данных из json формата в объект модели Employee и обратно в json формат.
    """

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data: dict) -> Employee:
        """
        Реализуем сохранение данных в БД
        """

        return Employee.objects.create(**validated_data)