"""
Unit tests for js_executor.py module.

Tests the JavaScript execution pool functionality including:
- Worker task execution
- Process pool initialization and reuse
- Timeout handling
- Error handling
- Graceful shutdown
"""

import pytest

from insights_content_template_renderer.js_executor import (
    _eval_js_worker_task,
    JsExecutor,
    get_js_executor,
    shutdown_js_executor,
)


def test_worker_task_successful_execution():
    """Test successful JavaScript execution in worker."""
    js_code = "(function(data) { return 'Hello ' + data.name; })"
    data = {"name": "World"}

    status, result = _eval_js_worker_task(js_code, data)

    assert status == "success"
    assert result == "Hello World"


def test_worker_task_runtime_error():
    """Test worker task with JavaScript runtime error."""
    js_code = "(function(data) { throw new Error('test error'); })"
    data = {}

    status, result = _eval_js_worker_task(js_code, data)

    assert status == "error"
    assert "test error" in result


def test_executor_initialization():
    """Test JsExecutor initialization."""
    executor = JsExecutor()

    assert executor._process_pool is None
    assert executor._timeout == 5


def test_lazy_pool_initialization():
    """Test that process pool is created lazily on first use."""
    executor = JsExecutor()

    # Pool should be None initially
    assert executor._process_pool is None

    # Get pool should create it
    pool = executor.get_pool()

    assert pool is not None
    assert executor._process_pool is not None

    pool.terminate()


def test_pool_reuse():
    """Test that get_pool returns the same pool instance."""
    executor = JsExecutor()

    pool1 = executor.get_pool()
    pool2 = executor.get_pool()

    assert pool1 is pool2

    pool1.terminate()


def test_execute_simple_function():
    """Test executing a simple JavaScript function."""
    executor = JsExecutor()
    js_code = "(function(data) { return 'test result'; })"

    result = executor.execute(js_code, {})

    assert result == "test result"

    executor.shutdown()


def test_execute_with_custom_timeout():
    """Test executing with custom timeout."""
    executor = JsExecutor()
    js_code = "(function(data) { return 'quick'; })"

    result = executor.execute(js_code, {}, timeout=1)

    assert result == "quick"

    executor.shutdown()


def test_execute_timeout_error():
    """Test that timeout raises TimeoutError."""
    executor = JsExecutor()
    # JavaScript function that runs forever
    js_code = "(function(data) { while(true) {} })"

    with pytest.raises(TimeoutError) as exc_info:
        executor.execute(js_code, {}, timeout=1)

    assert "timed out" in str(exc_info.value).lower()

    executor.shutdown()


def test_execute_javascript_error():
    """Test that JavaScript errors are raised as RuntimeError."""
    executor = JsExecutor()
    js_code = "(function(data) { throw new Error('JS error'); })"

    with pytest.raises(RuntimeError) as exc_info:
        executor.execute(js_code, {})

    assert "JS error" in str(exc_info.value)

    executor.shutdown()


def test_shutdown_with_no_pool():
    """Test shutdown when no pool was created."""
    executor = JsExecutor()

    # Should not raise any errors
    executor.shutdown()

    assert executor._process_pool is None


def test_shutdown_with_active_pool():
    """Test shutdown with an active pool."""
    executor = JsExecutor()

    # Create pool by executing something
    js_code = "(function(data) { return 'test'; })"
    executor.execute(js_code, {})

    # Shutdown should work cleanly
    executor.shutdown()


def test_sequential_executions_reuse_pool():
    """Test multiple sequential executions reuse the same pool."""
    executor = JsExecutor()
    js_code = "(function(data) { return data.value; })"

    # All executions should use the same pool
    pool_before = None
    for i in range(3):
        result = executor.execute(js_code, {"value": f"test{i}"})
        assert f"test{i}" in result

        if pool_before is None:
            pool_before = executor._process_pool
        else:
            # Pool should be reused
            assert executor._process_pool is pool_before

    executor.shutdown()


def test_multiple_different_executions():
    """Test executing different JavaScript functions sequentially."""
    executor = JsExecutor()

    js1 = "(function(data) { return data.x * 2; })"
    js2 = "(function(data) { return data.y + 10; })"
    js3 = "(function(data) { return data.z; })"

    result1 = executor.execute(js1, {"x": 5})
    result2 = executor.execute(js2, {"y": 3})
    result3 = executor.execute(js3, {"z": "hello"})

    # JavaScript numbers get converted to strings with decimal point
    assert result1 == "10.0"
    assert result2 == "13.0"
    assert result3 == "hello"

    executor.shutdown()


def test_get_js_executor_singleton():
    """Test that get_js_executor returns singleton JsExecutor instance."""
    executor1 = get_js_executor()
    executor2 = get_js_executor()

    assert isinstance(executor1, JsExecutor)
    assert executor1 is executor2

    shutdown_js_executor()


def test_shutdown_js_executor_cleans_up():
    """Test that shutdown_js_executor properly cleans up."""
    executor = get_js_executor()

    # Execute something to create pool
    js_code = "(function(data) { return 'test'; })"
    executor.execute(js_code, {})

    # Shutdown should work
    shutdown_js_executor()

    # After shutdown, getting executor again should create new instance
    new_executor = get_js_executor()
    assert new_executor is not executor

    shutdown_js_executor()


def test_shutdown_js_executor_with_no_executor():
    """Test shutdown when no executor was created."""
    # Should not raise any errors
    shutdown_js_executor()


def test_es7_array_includes():
    """Test that JS executor supports ES7 features (e.g. Array.includes method)."""
    executor = JsExecutor()

    template_js = """(function(data) {
        if (data.namespaces.includes('openshift-logging')) {
            return 'Found logging namespace';
        }
        return 'Not found';
    })"""

    data = {"namespaces": ["openshift-logging", "default", "kube-system"]}

    result = executor.execute(template_js, data)

    assert result == "Found logging namespace"

    executor.shutdown()
