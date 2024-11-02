import os
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from decimal import Decimal
from datetime import datetime
from collections import Counter

# Определение классов
# Класс хранит идентификатор и позицию в файле
class ModelIndex:
     def __init__(self, model_id: int, position_in_file_models: int):
        self.model_id = model_id
        self.position_in_file_models = position_in_file_models

class CarIndex:
    def __init__(self, car_id: str, position_in_file_cars: int):
        self.car_id = car_id
        self.position_in_file_cars = position_in_file_cars

class SaleIndex:
    def __init__(self, car_vin: str, position_in_file_sales: int):
        self.car_vin = car_vin
        self.position_in_file_sales = position_in_file_sales

class CarService:
    # Формирует полный путь к файлу, объединяя корневой путь и имя файла
    def _format_path(self, filename: str) -> str:
        return os.path.join(self.root_dir, filename)

    # Читает файл. Если файл нет, возвращается пустой список, иначе строки файла разделяются по запятой и возвращаются в виде списка списков
    def _read_file(self, filename: str) -> list[list[str]]:
        if not os.path.exists(self._format_path(filename)):
            return []
        else:
            with open(self._format_path(filename), 'r') as f:
                lines = f.readlines()
                split_lines = [l.strip().split(',') for l in lines]
                return split_lines

    def __init__(self, root_dir: str) -> None:
        self.root_dir = root_dir
        self.model_index: list[ModelIndex] = []
        self.car_index: list[CarIndex] = []
        self.sale_index: list[SaleIndex] = []

        split_model_lines = self._read_file("models_index.txt")
        self.model_index = [ModelIndex(int(l[0]), int(l[1])) for l in split_model_lines]

        split_car_lines = self._read_file('cars_index.txt')
        self.car_index = [CarIndex(str(l[0]), int(l[1])) for l in split_car_lines]

        split_sales_lines = self._read_file('sales_index.txt')
        self.sale_index = [SaleIndex(str(l[0]), int(l[1])) for l in split_sales_lines]

    # Находит информацию о модели по её идентификатору.
    # Ищет строку в файле models_index.txt, чтобы получить номер строки для соответствующей модели
    # Читает эту строку из файла models.txt, чтобы извлечь данные о модели и вернуть объект Model
    def _get_model_info(self, model_id: str) -> Model:
        with open(self._format_path('models_index.txt'), 'r') as f:
            for model_string in f:
                id, model_index = model_string .strip().split(',')
                if model_id == id:
                    target_string = int(model_index)
                    break
            else:
                raise ValueError('Model not found')
        with open(self._format_path('models.txt'), 'r') as f:
            f.seek(target_string * 502)
            model_arr = f.readline().strip().split(',')
        return Model(id=model_arr[0], name=model_arr[1], brand=model_arr[2])

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        with open(self._format_path("models.txt"), "a") as f:
            str_model = f'{model.id},{model.name},{model.brand}'.ljust(500)
            f.write(str_model + "\n")

        new_mi = ModelIndex(model.id, len(self.model_index))
        self.model_index.append(new_mi)
        self.model_index.sort(key=lambda x: x.model_id)

        with open(self._format_path("models_index.txt"), "w") as f:
            for current_mi in self.model_index:
                str_model = f"{current_mi.model_id},{current_mi.position_in_file_models}".ljust(50)
                f.write(str_model + "\n")

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        with open(self._format_path("cars.txt"), "a") as f:
            str_car = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
            f.write(str_car + "\n")

        new_ci = CarIndex(car.vin, len(self.car_index))
        self.car_index.append(new_ci)
        self.car_index.sort(key=lambda x: x.car_id)

        with open(self._format_path("cars_index.txt"), "w") as f:
            for current_mi in self.car_index:
                str_car = f"{current_mi.car_id},{current_mi.position_in_file_cars}".ljust(50)
                f.write(str_car + "\n")

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        with open(self._format_path("sales.txt"), "a") as f:
            str_sale = f"{sale.sales_number},{sale.car_vin},{sale.sales_date},{sale.cost}".ljust(500)
            f.write(str_sale + '\n')

        new_si = SaleIndex(sale.car_vin, len(self.sale_index))
        self.sale_index.append(new_si)
        self.sale_index.sort(key=lambda x: x.car_vin)

        with open(self._format_path("sales_index.txt"), "w") as f:
            for current_si in self.sale_index:
                string = f"{current_si.car_vin},{current_si.position_in_file_sales}".ljust(50)
                f.write(string + "\n")

        with open(self._format_path("cars_index.txt"), "r") as f:
            car_strings = f.readlines()
            target_string = -1
            for car_string in car_strings:
                vin, car_index = car_string.strip().split(",")
                if vin == sale.car_vin:
                    target_string = int(car_index)
                    break
            if target_string == -1:
                raise Exception('Car not found')

        with open(self._format_path("cars.txt"), "r+") as f:
            f.seek(target_string * 502)
            car_string = f.readline()
            car_arr = car_string.strip().split(",")

            car = Car(vin=str(car_arr[0]),
                      model=int(car_arr[1]),
                      price=Decimal(car_arr[2]),
                      date_start=datetime.strptime(car_arr[3], "%Y-%m-%d %H:%M:%S"),
                      status=CarStatus(car_arr[4]))
            car.status = CarStatus.sold

            f.seek(target_string * 502)
            f.write(f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500) + "\n")

        return car

    # Задание 3.  Вывод машин, доступных к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        list = []
        with open(self._format_path("cars.txt"), "r") as file:
            lines = file.readlines()
            for line in lines:
                vin, model, price, date_start, car_status = line.strip().split(",")
#                car = Car(
#                    vin=parts[0],
#                    model=int(parts[1]),
#                    price=Decimal(parts[2]),
#                    date_start=datetime.strptime(parts[3], "%Y-%m-%d %H:%M:%S"),
#                    status=CarStatus(parts[4]))
#                if car.status == status:
#                    list.append(car)

#                if parts[-1] == status:
#                    car = Car(
#                        vin=parts[0],
#                        model=int(parts[1]),
#                        price=Decimal(parts[2]),
#                        date_start=datetime.strptime(parts[3], "%Y-%m-%d %H:%M:%S"),
#                        status=CarStatus(parts[-1]))
#                    list.append(car)
                if car_status.strip() == status.value:
                    car = Car(
                        vin=vin,
                        model=int(model),
                        price=Decimal(price),
                        date_start=datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S"),
                        status=CarStatus(car_status.strip())
                    )
                    list.append(car)
#       list.sort(key=lambda car: car.vin)
#       list = sorted(list, key=lambda car: car.vin)
        return list

    # Задание 4. Вывод детальной информации
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        with open(self._format_path("cars_index.txt"), "r") as f:
            car_strings = f.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    target_string = int(car_index)
                    break
            if target_string == -1:
                return None

        with open(self._format_path("cars.txt"), "r") as f:
            f.seek(target_string * 502)
            car_string = f.readline()
            car_arr = car_string.strip().split(",")
        model_id = int(car_arr[1])

        with open(self._format_path("models_index.txt"), "r") as f:
            model_strings = f.readlines()
            target_string = -1
            for model_string in model_strings:
                id, model_index = model_string.strip().split(",")
                if model_id == int(id):
                    target_string = int(model_index)
                    break
            if target_string == -1:
                return None

        with open(self._format_path("models.txt"), "r") as f:
            f.seek(target_string * 502)
            model_string = f.readline()
            model_arr = model_string.strip().split(",")

        if str(car_arr[4]) != CarStatus.sold:
            sales_date = None
            sales_cost = None

        else:
            with open(self._format_path("sales_index.txt"), "r") as f:
                sale_strings = f.readlines()
                target_string = -1
                for sale_string in sale_strings:
                    car_vin, sale_index = sale_string.strip().split(",")
                    if car_vin == vin:
                        target_string = int(sale_index)
                        break
                if target_string == -1:
                    return None

            with open(self._format_path("sales.txt"), "r") as f:
                f.seek(target_string * 502)
                sale_string = f.readline()
                sale_arr = sale_string.strip().split(",")

                sales_date = datetime.strptime(sale_arr[2], "%Y-%m-%d %H:%M:%S")
                sales_cost = Decimal(sale_arr[3])

        return CarFullInfo(vin=str(car_arr[0]),
                           car_model_name=str(model_arr[1]),
                           car_model_brand=str(model_arr[2]),
                           price=Decimal(car_arr[2]),
                           date_start=datetime.strptime(car_arr[3], "%Y-%m-%d %H:%M:%S"),
                           status=CarStatus(car_arr[4]),
                           sales_date=sales_date,
                           sales_cost=sales_cost)

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        with open(self._format_path("cars_index.txt"), "r") as f:
            car_strings = f.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    target_string = int(car_index)
                    break
            if target_string == -1:
                raise Exception('Car not found')

        with open(self._format_path("cars.txt"), "r+") as f:
            f.seek(target_string * 502)
            car_string = f.readline()
            car_arr = car_string.strip().split(",")
            car_arr[0] = new_vin

            f.seek(target_string * 502)
            string = ",".join(car_arr).ljust(500)
            f.write(string + "\n")

        for index in self.car_index:
            if index.car_id == vin:
                index.car_id = new_vin

        self.car_index.sort(key=lambda x: x.car_id)

        with open(self._format_path("cars_index.txt"), "w") as f:
            for current_ci in self.car_index:
                string = f"{current_ci.car_id},{current_ci.position_in_file_cars}".ljust(50)
                f.write(string + "\n")

        car = Car(vin=new_vin,
                  model=int(car_arr[1]),
                  price=Decimal(car_arr[2]),
                  date_start=datetime.strptime(car_arr[3], "%Y-%m-%d %H:%M:%S"),
                  status=CarStatus(car_arr[4]))

        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        target_string = -1
        vin = None

        with open(self._format_path("sales.txt"), "r") as f:
            sale_string = f.readlines()
            for sale_index, sale_string in enumerate(sale_string):
                sales_num, car_vin, _, _ = sale_string.strip().split(",")
                if sales_num == sales_number:
                    vin = car_vin
                    target_line = sale_index
                    break
        if target_line == -1:
            raise Exception('Sale not found')

        with open(self._format_path("cars_index.txt"), "r") as index_file:
            car_strings = index_file.readlines()
            target_string = -1
            for car_string in car_strings:
                car_id, car_index = car_string.strip().split(",")
                if car_id == vin:
                    target_string = int(car_index)
                    break
        if target_string == -1:
            raise Exception('Car not found')

        with open(self._format_path("cars.txt"), "r+") as f:
            f.seek(target_string * 502)
            car_string = f.readline()
            car_arr = car_string.strip().split(",")

            car = Car(vin=str(car_arr[0]),
                      model=int(car_arr[1]),
                      price=Decimal(car_arr[2]),
                      date_start=datetime.strptime(car_arr[3], "%Y-%m-%d %H:%M:%S"),
                      status=CarStatus(car_arr[4]))
            car.status = CarStatus.available

            f.seek(target_string * 502)
            f.write(f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500) + "\n")

        with open(self._format_path("sales.txt"), "w") as f:
            for sale_index, sale_string in enumerate(sale_string):
                if sale_index != target_line:
                    f.write(sale_string)

        with open(self._format_path("sales.txt"), "r") as f:
            sale_string = f.readlines()

        sales_index = []
        for sale_index, sale_string in enumerate(sale_string):
            _, car_vin, _, _ = sale_string.strip().split(",")
            sales_index.append((car_vin, sale_index))

        sales_index.sort(key=lambda x: x[0])

        with open(self._format_path("sales_index.txt"), "w") as index_file:
            for car_vin, sale_index in sales_index:
                index_file.write(f"{car_vin},{sale_index}".ljust(50) +"\n")

        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        with open(self._format_path("sales_index.txt"), "r") as f:
            sale_strings = f.readlines()

        with open(self._format_path("cars_index.txt"), "r") as f:
            car_index_data = {car_vin: int(car_index) for car_vin, car_index in (line.strip().split(",") for line in f)}

        with open(self._format_path("cars.txt"), "r") as f:
            car_data = f.readlines()

        model_id_list = []

        for sale_string in sale_strings:
            car_vin = sale_string.strip().split(",")[0]
            if car_vin in car_index_data:
                target_string = car_index_data[car_vin]
                car_string = car_data[target_string]
                model_id = car_string.strip().split(",")[1]
                model_id_list.append(model_id)

        top_models = Counter(model_id_list)
        top_3_models = top_models.most_common(3)

        result = [
            ModelSaleStats(car_model_name=str(self._get_model_info(model_id).name),
                           brand=self._get_model_info(model_id).brand,
                           sales_number=sales_number) for model_id, sales_number in top_3_models
        ]

        return result
