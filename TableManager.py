class RegulatorTableManager(BaseTableManager):
    
    def get_columns(self):
        return ["regulator", "kv", "lines_count"]

class BoilerTableManager(BaseTableManager):
    def get_columns(self):
        return ["boiler_power", "gas_temp_in", "gas_temp_out"]

class PipeTableManager(BaseTableManager):
    def get_columns(self):
        return ["pipe_diameter", "wall_thickness", "gas_speed", "gas_temperature", "lines_count"]

class TableFactory:








class BaseTableManager(ABC):
    def __init__(self,parent,table_type):
        self.parent = parent
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        self.table_type = table_type

    @abstractmethod
    def get_columns(self) -> list:
        pass
    
    def get_table_type(self) -> str:
        return self.table_type
    
    def create_table(self,table_name):#Перенести в model
        """Create table in databaze"""
            # Логирование начала создания таблицы
        logger.info(f"Начинаем создание таблицы '{table_name}'")
        try:
            # Получаем список колонок из подкласса
            columns = self.get_columns()
            logger.debug(f"Получены колонки: {columns}")

            # Проверяем, что колонки не пустые
            if not columns:
                logger.error("Список колонок пуст!")
                raise ValueError("Колонки не определены")

            # # Формируем SQL-запрос для создания таблицы
            # create_table_query = f'''
            #     CREATE TABLE IF NOT EXISTS '{table_name}' (
            #         {", ".join([f"{col} REAL" for col in columns])}
            #     )
            # '''
            # logger.debug(f"SQL-запрос создания таблицы: {create_table_query}")

            # # Формируем SQL-запрос для вставки данных
            # insert_query = f'''
            #     INSERT INTO '{table_name}' ({", ".join(columns)}) 
            #     VALUES ({", ".join(["?"] * len(columns))})
            # '''
            # logger.debug(f"SQL-запрос вставки данных: {insert_query}")

            # Подключаемся к базе данных
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Выполняем создание таблицы
                logger.info(f"Выполняем создание таблицы '{table_name}' в базе данных")
                cursor.execute(create_table_query)
                logger.debug("Таблица успешно создана или уже существует")

                # Выполняем вставку пустых данных для инициализации
                logger.info("Выполняем вставку пустых данных для инициализации таблицы")
                cursor.execute(insert_query, [""] * len(columns))
                logger.debug("Данные успешно вставлены")

        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка SQLite при создании таблицы '{table_name}': {e}")
            logger.error(f"Запрос: {create_table_query}")
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {e}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при создании таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            logger.info(f"Таблица '{table_name}' успешно создана и инициализирована")
        
    def load_table(self, table_name): #Перенести в data_model
        """Загружает данные таблицы в Treeview."""
        logger.info(f"Начинаем загрузку данных таблицы '{table_name}'")
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
                logger.debug(f"Загружены данные: \n{df.to_string()}")
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=list(row))
            logger.info(f"Данные таблицы '{table_name}' успешно загружены")

        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка загрузки таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")

        except Exception as e:
            logger.exception(f"Неожиданная ошибка при загрузке таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def save_data(self, tree, table_name,window): #Перенести в data_model
        """Сохраняет данные из Treeview в базу данных."""
        logger.info(f"Начинаем сохранение данных таблицы '{table_name}'")
        try:
            data = [tree.item(item)["values"] for item in tree.get_children()]
            logger.debug(f"Данные для сохранения: {data}")
            columns = self.get_columns()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM '{table_name}'")
                cursor.executemany(f"INSERT INTO '{table_name}' VALUES ({', '.join(['?']*len(columns))})", data)
            logger.info(f"Данные таблицы '{table_name}' успешно сохранены")
            showinfo("Успех","Данные успешно сохранены")
            window.destroy()
        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка сохранения таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить таблицу: {e}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при сохранении таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
    
    def add_editing_features(self,event):
        """Обработка двойного клика для редактирования ячейки."""
        # Получаем выбранную строку и столбец
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        # Получаем ID строки и имя столбца
        item_id = self.tree.focus()
        column = self.tree.identify_column(event.x)
        column_index = int(column[1:]) - 1  # Индекс столбца (начиная с 0)

        # Значение текущей ячейки
        current_value = self.tree.item(item_id)["values"][column_index]

        # Создаем Entry для редактирования
        entry = ttk.Entry(self.tree)
        entry.insert(0, str(current_value))
        entry.focus()

        # Размещение Entry поверх ячейки
        x, y, width, height = self.tree.bbox(item_id, column)
        entry.place(x=x, y=y, width=width, height=height)

        # Обработка завершения редактирования
        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item_id)["values"])
            values[column_index] = new_value
            self.tree.item(item_id, values=values)
            entry.destroy()
        entry.bind("<Return>", save_edit)  # Сохранение при нажатии Enter
        entry.bind("<FocusOut>", save_edit)  # Сохранение при потере фокуса

    def open_table_window(self, table_name):# Перенести в Gui
        """Открывает окно с таблицей."""
        logger.info(f"Открытие окна таблицы '{table_name}'")
        try:
            window = tk.Toplevel(self.parent)
            window.title(f"Таблица: {table_name}")
            logger.debug(f"Создано новое окно для таблицы '{table_name}'")

            self.tree = ttk.Treeview(window, columns=self.get_columns(), show="headings")
            for col in self.get_columns():
                self.tree.heading(col, text=col)
            self.tree.pack(fill="both", expand=True)
            logger.debug("Treeview инициализирован с колонками")

            self.load_table(table_name)
            logger.debug("Данные загружены в Treeview")

            save_button = ttk.Button(
                window,
                text="Сохранить данные",
                command=lambda: self.save_data(self.tree, table_name,window)
            )
            save_button.pack(pady=10)
            logger.debug("Кнопка сохранения добавлена в окно")

            self.tree.bind("<Double-1>", self.add_editing_features)
            logger.debug("Событие двойного клика привязано к редактированию ячеек")

        except Exception as e:
            logger.exception(f"Ошибка при открытии окна таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Не удалось открыть таблицу: {e}")


class TableFactory:
    @staticmethod
    def create_table_manager(table_type, parent):
        logger.info(f"Запрос на создание менеджера таблицы типа: '{table_type}'")
        logger.debug(f"Параметры: parent={parent}")

        match table_type:
            case "Таблица для регуляторов":
                logger.info("Создан менеджер таблицы регуляторов")
                return RegulatorTableManager(parent,table_type)
            
            case "Таблица котельной":
                logger.info("Создан менеджер таблицы котельной")
                return BoilerTableManager(parent,table_type)
            
            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                logger.info(f"Создан менеджер таблицы труб: {table_type}")
                return PipeTableManager(parent,table_type)
            
            case _:
                error_msg = f"Неизвестный тип таблицы: {table_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

class TableManager:
    def __init__(self, parent, data_model):
        logger.info("Инициализация TableManager")
        self.parent = parent
        self.data_model = data_model
        self.tables = {}  # Хранит все таблицы: {"table_name": manager}
        logger.debug("Создание виджетов для управления таблицами")
        self.create_widgets()
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора"
        ]
        logger.debug(f"Список доступных типов таблиц: {self.table_labels}")
        self.row = 4

    def create_widgets(self):
        logger.info("Создание кнопки 'Исходные таблицы'")
        input_table_button = ttk.Button(
            self.parent,
            text="Исходные таблицы",
            command=self.check_table_func
        )
        input_table_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        logger.debug("Кнопка 'Исходные таблицы' размещена в интерфейсе")

    def create_window_table(self):
        logger.info("Создание окна выбора таблиц")
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Таблицы граничных условий")
        logger.debug("Окно таблиц создано")
        
        # Метка для выбора таблицы
        label = WidgetFactory.create_label(self.table_window, "Выберите таблицу:", 0)
        logger.debug("Метка 'Выберите таблицу' добавлена в окно")

        # Combobox
        self.combobox = ttk.Combobox(
            self.table_window,
            values=self.table_labels,
            state="readonly",
            width=33
        )
        self.combobox.grid(row=1, column=0, padx=5, pady=5)
        logger.debug(f"Combobox инициализирован с вариантами: {self.table_labels}")

        # Кнопка добавления таблицы
        save_button = WidgetFactory.create_Button(
            self.table_window,
            "Добавить таблицу",
            2,
            self.define_table
        )
        logger.debug("Кнопка 'Добавить таблицу' добавлена в окно")

    def check_table_func(self):
        logger.info("Вызов метода check_table_func")
        if len(self.tables) == 0:
            logger.warning("Список таблиц пуст. Создаем новое окно.")
            self.create_window_table()
        else:
            logger.info("Список таблиц не пуст. Обновляем окно.")
            self.create_window_table()
            for name in self.tables:
                logger.debug(f"Добавление метки для таблицы: {name}")
                print(f"{self.tables=}")
                label = WidgetFactory.create_label(
                    self.table_window,
                    self.tables[name].get_table_type(),
                    self.row
                )
                entry = WidgetFactory.create_entry(self.table_window, self.row, 1)
                entry.insert(0, name)
                open_button = WidgetFactory.create_Button(
                    parent =self.table_window,
                    label_text="Открыть таблицу",
                    row=self.row,
                    function=lambda tn=name, tt=self.tables[name].get_table_type(): self.open_table(tn, tt),
                    column=3
                )
                self.row += 1
                logger.debug(f"Метка и кнопка для таблицы '{name}' добавлены в окно")

    def define_table(self):
        logger.info("Начало определения новой таблицы")
        selection = self.combobox.get()
        if not selection:
            logger.error("Тип таблицы не выбран")
            print("Ошибка: Таблица не выбрана!")
            return
        logger.debug(f"Выбранный тип таблицы: {selection}")
        self.row += 1

        # Метка с названием таблицы
        logger.debug("Создание метки для нового типа таблицы")
        label = WidgetFactory.create_label(
            self.table_window,
            label_text=selection,
            row=self.row
        )

        # Поле ввода имени таблицы
        logger.debug("Создание поля ввода имени таблицы")
        entry = WidgetFactory.create_entry(self.table_window, self.row, 1)

        # Кнопка для открытия таблицы
        open_button = WidgetFactory.create_Button(
            self.table_window,
            "Открыть таблицу",
            self.row,
            lambda: self.open_table(entry.get(), selection),
            3
        )
        logger.info("Интерфейс для создания/открытия таблицы инициализирован")

    def add_table(self, table_name, table_type):
        logger.info(f"Попытка добавления таблицы '{table_name}' типа '{table_type}'")
        
        if table_name  == "":
            messagebox.showwarning("Ошибка", "Введите название таблицы")
            return

        if table_name in self.tables:
            logger.warning(f"Таблица '{table_name}' уже существует")
            messagebox.showwarning("Ошибка", f"Таблица '{table_name}' уже существует!")
            return
        
        logger.debug("Создание менеджера таблицы через TableFactory")
        manager = TableFactory.create_table_manager(table_type, self.parent)
        manager.create_table(table_name)
        print(f"{manager=}")
        self.tables[table_name] = manager
        self.data_model.set_tables_data(self.tables)
        logger.info(f"Таблица '{table_name}' добавлена в реестр")

    def open_table(self, table_name, table_type):
        logger.info(f"Попытка открытия таблицы '{table_name}' типа '{table_type}'")
        if table_name not in self.tables:
            logger.warning(f"Таблица '{table_name}' не найдена. Создаем новую.")
            self.add_table(table_name, table_type)
  
        logger.debug("Открытие окна таблицы через менеджер")
        self.tables[table_name].open_table_window(table_name)
        logger.info(f"Таблица '{table_name}' открыта")


