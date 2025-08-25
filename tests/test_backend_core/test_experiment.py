import pytest
from backend.db.interface import GetDataBaseInterface

database = GetDataBaseInterface()

@pytest.mark.asyncio
async def test_get_experiment():
    test_data = ('LRX20250825c3106917', 'e1')

    data = await database.get_experiment(test_data)
    print(data, type(data))