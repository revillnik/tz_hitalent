from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator



class Department(models.Model):
    """
    Класс, описывающий таблицу department в БД
    """

    name = models.CharField(validators=[MinLengthValidator(1), MaxLengthValidator(200)], null=False, verbose_name='название подразделения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')

    parent_id = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        related_name='parent', 
        verbose_name='родительское подразделение'
        )

    def __str__(self) -> str:
        return self.name


class Employee(models.Model):
    """
    Класс, описывающий таблицу employee в БД
    """

    full_name = models.CharField(validators=[MinLengthValidator(1), MaxLengthValidator(200)], null=False, verbose_name='ФИО')
    position = models.CharField(validators=[MinLengthValidator(1), MaxLengthValidator(200)], null=False, verbose_name='должность')
    hired_at = models.DateField(null=True, verbose_name='дата найма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')
    
    department_id = models.ForeignKey(
        'Department', 
        on_delete=models.CASCADE, 
        related_name='department',
        verbose_name='подразделение сотрудника'
        )

    def __str__(self) -> str:
        return self.full_name


