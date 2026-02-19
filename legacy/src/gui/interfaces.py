from abc import abstractmethod,ABC


class MessageHandler_Interfaces(ABC):
    """Интерфейс для обработки сообщений об успехе или ошибке"""
    @abstractmethod
    def show_success(self, message: str):
        """Показать сообщение об успехе"""
        raise NotImplementedError

    @abstractmethod
    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        raise NotImplementedError

    @abstractmethod
    def show_warning(self, message: str):
        """Показать предупреждение"""
        raise NotImplementedError





