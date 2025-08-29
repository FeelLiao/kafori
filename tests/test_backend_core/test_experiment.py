import pytest
from backend.db.interface import GetDataBaseInterface as database
from backend.db.interface import PutDataBaseInterface as put_db
import pandas as pd


@pytest.mark.asyncio
async def test_get_experiment():
    test_data = ('LRX20250825c3106917', 'e1')

    data = await database.get_experiment(test_data)
    print(data, type(data))

@pytest.mark.asyncio
async def test_put_experiment():
    test_data = {
        'UniqueEXID': ['5', '6'],
        'ExpClass': ['LRX20250825c3106917', 'e1'],
        'Experiment': ['LRX20250825c3106917', 'e1'],
    }

    data = await put_db.put_experiment(pd.DataFrame(test_data))
    print(data, type(data))