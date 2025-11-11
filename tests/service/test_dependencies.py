from syntaxis.api import Syntaxis
from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service, get_syntaxis


def test_get_syntaxis_returns_instance():
    """get_syntaxis returns Syntaxis instance."""
    syntaxis = get_syntaxis()
    assert isinstance(syntaxis, Syntaxis)
    assert syntaxis.database is not None
    assert syntaxis.template is not None


def test_get_syntaxis_uses_default_db_path():
    """get_syntaxis uses ./syntaxis.db by default."""
    syntaxis = get_syntaxis()
    assert syntaxis.database._db_path == "./syntaxis.db"


def test_get_service_returns_instance():
    """get_service returns SyntaxisService instance."""
    syntaxis = get_syntaxis()
    service = get_service(syntaxis)
    assert isinstance(service, SyntaxisService)
    assert service.syntaxis is syntaxis


def test_get_service_with_custom_syntaxis():
    """get_service accepts custom Syntaxis instance."""
    custom_syntaxis = Syntaxis(db_path="./test.db")
    service = get_service(custom_syntaxis)
    assert service.syntaxis is custom_syntaxis
