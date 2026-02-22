# Список допустимых команд. Проверка "cmd in COMMANDS".
# Вызов метода делается в DomainCLI.run() по имени команды на переданном экземпляре app.
COMMANDS = frozenset({
    "add", "start", "cancel", "complete", "list",
    "edit", "clear", "delete", "show", "exit"
})

EDIT_COMMANDS = frozenset({"id", "title", "description", "deadline", "all"})