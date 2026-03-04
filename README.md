Данный проект является тестовым заданием для компании hitalent.  
Хочу отметить, что в проекте использовался DRF, реализованы тесты, Dockerfile для проекта, docker-compose для запуска контейнеров в единой сети с БД postgres  

Для запуска следует прописать команду (в папке с проектом):  
docker-compose up   

Были реализованы все необходимые API методы:  
1) Создать подразделение
POST /departments/  
- Body:
  * name: str  
  * parent_id: int | null (опционально)  
- Response: созданное подразделение  

2) Создать сотрудника в подразделении
POST /departments/{id}/employees/ 
- Body:
  * full_name: str  
  * position: str  
  * hired_at: date | null (опционально)  
- Response: созданный сотрудник  

3) Получить подразделение (детали + сотрудники + поддерево)  
GET /departments/{id}  
- Query:
  * depth: int (по умолчанию 1, максимум 5) — глубина вложенных подразделений в ответе  
  * include_employees: bool (по умолчанию true)  
- Response:
  * department (объект подразделения)  
  * employees: [] (если include_employees=true, сортировка по created_at или full_name)  
  * children: [] (вложенные подразделения до depth, рекурсивно)  

4) Переместить подразделение в другое (изменить parent)    
PATCH /departments/{id}  
- Body:
  * name: str (опционально)  
  * parent_id: int | null (опционально)  
- Response: обновлённое подразделение  

5) Удалить подразделение
DELETE /departments/{id}  
- Query:
  * mode: str (cascade | reassign)  
  * cascade — удалить подразделение, всех сотрудников и все дочерние подразделения  
  * reassign — удалить подразделение, а сотрудников перевести в reassign_to_department_id  
  * reassign_to_department_id: int (обязателен, если mode=reassign)  
- Response: 204 No Content (или json-статус)  

