import pytest
import types

import backend.analysis.analysis_base as analysis_base


@pytest.fixture
def rprocessor_mp(monkeypatch):
    # Patch Pool to avoid creating real processes
    class DummyPool:
        def apply(self, func, args, kwargs):
            return func(*args, **kwargs)

        def close(self): pass
        def join(self): pass
    monkeypatch.setattr(analysis_base, "Pool", lambda *a, **kw: DummyPool())
    # Patch R initialization
    monkeypatch.setattr(analysis_base.RProcessorPoolMP,
                        "_init_r", staticmethod(lambda: None))
    # Patch rpy2.robjects

    class DummyR:
        def __call__(self, code):
            return f"executed: {code}"

        def setenv(self, env): pass
        def __getitem__(self, key): return None
    monkeypatch.setattr(analysis_base, "ro", types.SimpleNamespace(
        r=DummyR(),
        globalenv={},
        Environment=lambda: {},
        RObject=str
    ))
    return analysis_base.RProcessorPoolMP(pool_size=2)


def test_run_analysis_basic(rprocessor_mp):
    result = rprocessor_mp.run_analysis("1+1")
    assert result == "executed: 1+1"


def test_run_analysis_with_kwargs(rprocessor_mp):
    result = rprocessor_mp.run_analysis("x+1", x=5)
    assert result == "executed: x+1"
    assert rprocessor_mp.pool is not None


def test_close_pool(rprocessor_mp):
    rprocessor_mp.close()
    assert rprocessor_mp.pool is None


@pytest.mark.asyncio
async def test_async_run_analysis_success(rprocessor_mp):
    result = await rprocessor_mp.async_run_analysis("2+2")
    assert result == "executed: 2+2"


def test_isolated_r_environment(monkeypatch):
    # Patch rpy2.robjects
    monkeypatch.setattr(analysis_base, "ro", types.SimpleNamespace(
        globalenv={},
        Environment=lambda: {},
        r=types.SimpleNamespace(setenv=lambda env: None,
                                __call__=lambda code: None)
    ))
    with analysis_base.RProcessorPoolMP._isolated_r_environment() as env:
        assert isinstance(env, dict)


@pytest.fixture
def rprocessor_cppe(monkeypatch):
    # Patch ProcessPoolExecutor to avoid creating real processes
    class DummyExecutor:
        def submit(self, func, *args, **kwargs):
            class DummyFuture:
                def result(self, timeout=None): return func(*args, **kwargs)
            return DummyFuture()

        def shutdown(self, wait=True): pass
    monkeypatch.setattr(analysis_base, "ProcessPoolExecutor",
                        lambda *a, **kw: DummyExecutor())
    # Patch R initialization
    monkeypatch.setattr(analysis_base.RProcessorPoolCPPE,
                        "_init_r", staticmethod(lambda: None))
    # Patch rpy2.robjects

    class DummyR:
        def __call__(self, code):
            return f"executed: {code}"

        def setenv(self, env): pass
    monkeypatch.setattr(analysis_base, "ro", types.SimpleNamespace(
        r=DummyR(),
        globalenv={},
        Environment=lambda: {},
        RObject=str
    ))
    return analysis_base.RProcessorPoolCPPE(pool_maxsize=2)


@pytest.mark.asyncio
async def test_cppe_async_run_analysis_success(rprocessor_cppe):
    result = await rprocessor_cppe.async_run_analysis("3+3")
    assert result == "executed: 3+3"


def test_cppe_close_executor(rprocessor_cppe):
    rprocessor_cppe.close()
    assert rprocessor_cppe.executor is None


def test_data_analysis_abstract():
    class DummyAnalysis(analysis_base.DataAnalysis):
        def run_analysis(self): return "ok"
    da = DummyAnalysis()
    assert da.run_analysis() == "ok"
