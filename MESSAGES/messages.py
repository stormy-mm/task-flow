from colorama import Style, Fore


class Messages:
    """Класс сообщений"""
    GREETING = ("Добро пожаловать в TaskFlow!\n\n"
                "Доступные команды:\n"
                f"{Fore.YELLOW}- add {Style.RESET_ALL}(Добавить задачу)\n"
                f"- start <id>(Начать задачу по id)\n"
                f"{Fore.GREEN}- complete <id> {Style.RESET_ALL}(Отметить задачу выполненной по id)\n"
                f"{Fore.RED}- cancel <id> {Style.RESET_ALL}(Отменить задачу по id)\n"
                f"{Fore.RED}- delete <id> {Style.RESET_ALL}(Удалить задачу по id)\n"
                f"{Fore.YELLOW}- edit <id> {Style.RESET_ALL}(Изменить информацию по id)\n"
                f"    {Fore.GREEN}- id <id> {Style.RESET_ALL}(id задачи)\n"
                f"    {Fore.GREEN}- title <title> {Style.RESET_ALL}(Название задачи)\n"
                f"    {Fore.GREEN}- description <description> {Style.RESET_ALL}(Описание задачи)\n"
                f"    {Fore.GREEN}- deadline <deadline> {Style.RESET_ALL}(Дедлайн задачи)\n"
                f"{Fore.YELLOW}- show <id> {Style.RESET_ALL}(Показать информацию о задаче по id)\n"
                f"{Fore.YELLOW}- list {Style.RESET_ALL}(Вывести список задач)\n"
                f"{Fore.RED}- clear {Style.RESET_ALL}(Очистить список задач)\n"
                f"{Fore.YELLOW}- exit {Style.RESET_ALL}(Выход из программы)\n\n"
                "Ввод команды")

    UNKNOW_COMMAND = f"{Fore.RED}Неизвестная команда{Style.RESET_ALL}"
    NOTFOUND_TASK = f"{Fore.RED}Задача не найдена{Style.RESET_ALL}"

    ADD_TASK = (
        f"\n{Style.BRIGHT}Введите id >>>  ",
        f"Введите название >>>  ",
        f"Введите описание (В случае отсутствия описания нажмите {Fore.LIGHTCYAN_EX}Enter{Style.RESET_ALL}) >>>  ",
        f"{Style.BRIGHT}{Fore.LIGHTRED_EX}ВАЖНАЯ ИНФОРМАЦИЯ{Style.RESET_ALL}{Style.BRIGHT}: "
        f"дедлайн должен быть в формате ДД ММ ГГГГ ЧЧ ММ СС (12 1 2025 8 0)\n"
        f"Введите дедлайн (В случае отсутствия дедлайна нажмите {Fore.LIGHTCYAN_EX}Enter{Style.RESET_ALL}) >>>  ",
    )