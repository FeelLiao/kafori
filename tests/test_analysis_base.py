import pytest
import asyncio
from backend.analysis.analysis_base import RProcessorPoolCPPE, RProcessorPoolMP

TEST_R_CODE1 = """
list(a = 1, b = 2)
"""

TEST_R_CODE2 = """
list(a = 3, b = 4)
"""

test_r_with_parm = "list(a,b)"


@pytest.mark.asyncio
async def test_async_run_analysis_success_mp(code: str = TEST_R_CODE1):
    processor = RProcessorPoolMP(pool_maxsize=2)
    try:
        result = await processor.run_analysis(code)
        assert result.rx2('a')[0] == 1
        assert result.rx2('b')[0] == 2
    finally:
        processor.close()


@pytest.mark.asyncio
async def test_async_run_analysis_with_parm_mp(code: str = test_r_with_parm):
    processor = RProcessorPoolMP(pool_maxsize=2)
    try:
        result = await processor.run_analysis(code, a=1, b=2)
        assert result.rx2(1)[0] == 1
        assert result.rx2(2)[0] == 2
    finally:
        processor.close()


@pytest.mark.asyncio
async def test_async_run_analysis_mp_multi(code1: str = TEST_R_CODE1,
                                           code2: str = TEST_R_CODE2):
    processor = RProcessorPoolMP(pool_maxsize=2)
    try:
        # 并发提交多个任务
        tasks = [
            processor.run_analysis(code1),
            processor.run_analysis(code2)
        ]
        results = await asyncio.gather(*tasks)
        # 断言每个结果
        assert results[0].rx2('a')[0] == 1
        assert results[0].rx2('b')[0] == 2
        assert results[1].rx2('a')[0] == 3
        assert results[1].rx2('b')[0] == 4
    finally:
        processor.close()


@pytest.mark.asyncio
async def test_async_run_analysis_success_cppe(code: str = TEST_R_CODE1):
    processor = RProcessorPoolCPPE(pool_maxsize=2)
    try:
        result = await processor.run_analysis(code)
        assert result.rx2('a')[0] == 1
        assert result.rx2('b')[0] == 2
    finally:
        processor.close()


@pytest.mark.asyncio
async def test_async_run_analysis_with_parm_cppe(code: str = test_r_with_parm):
    processor = RProcessorPoolCPPE(pool_maxsize=2)
    try:
        result = await processor.run_analysis(code, a=1, b=2)
        assert result.rx2(1)[0] == 1
        assert result.rx2(2)[0] == 2
    finally:
        processor.close()


@pytest.mark.asyncio
async def test_async_run_analysis_cppe_multi(code1: str = TEST_R_CODE1,
                                             code2: str = TEST_R_CODE2):
    processor = RProcessorPoolCPPE(pool_maxsize=2)
    try:
        # 并发提交多个任务
        tasks = [
            processor.run_analysis(code1),
            processor.run_analysis(code2)
        ]
        results = await asyncio.gather(*tasks)
        # 断言每个结果
        assert results[0].rx2('a')[0] == 1
        assert results[0].rx2('b')[0] == 2
        assert results[1].rx2('a')[0] == 3
        assert results[1].rx2('b')[0] == 4
    finally:
        processor.close()
