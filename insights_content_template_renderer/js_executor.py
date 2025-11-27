"""
JavaScript execution pool for running JS code in an isolated process.

This module provides a process pool for executing JavaScript code using PythonMonkey.
Running JS in the separate process avoids the PythonMonkey FastAPI recursion bug
(see https://github.com/Distributive-Network/PythonMonkey/issues/490).
"""

import logging
import multiprocessing as mp


log = logging.getLogger(__name__)


def _eval_js_worker_task(js_code, data):
    """
    Execute JavaScript in a worker process.
    This function is called by pool workers and returns the result directly.

    :param js_code: JavaScript code to execute
    :param data: Data to pass to the JavaScript function
    :return: Tuple of (status, result) where status is 'success' or 'error'
    """
    try:
        import pythonmonkey as pm
        func = pm.eval(js_code)
        result = func(data)
        # Convert to native Python string to avoid pickling issues
        # PythonMonkey returns JS strings that can't be pickled
        result_str = str(result) if result is not None else ''
        return ('success', result_str)
    except Exception as e:
        import traceback
        return ('error', f"{str(e)}\n{traceback.format_exc()}")


class JsExecutor:
    """
    Manages a process pool for executing JavaScript code in isolated processes.

    This class provides a singleton-style process pool that is lazily initialized
    on first use. Each uvicorn worker gets its own pool with a single worker process.
    """

    def __init__(self):
        """Initialize the JsExecutor with no process pool (lazy initialization)."""
        self._process_pool = None
        self._pool_lock = mp.Lock()
        self._timeout = 5  # Default timeout in seconds

    def get_pool(self):
        """
        Get or create the process pool for JavaScript execution.
        Uses lazy initialization to avoid creating processes during module import.

        Uses a single worker process since each uvicorn worker has its own pool.

        :return: The process pool instance
        """
        if self._process_pool is None:
            with self._pool_lock:
                # Double-check pattern to avoid race conditions
                if self._process_pool is None:
                    log.info("Initializing JavaScript worker process")

                    # Use spawn method to avoid inheriting FastAPI context
                    ctx = mp.get_context('spawn')
                    self._process_pool = ctx.Pool(processes=1)

                    log.info("JavaScript worker process initialized successfully")

        return self._process_pool

    def execute(self, js_code, data, timeout=None):
        """
        Execute JavaScript code with the given data in a worker process.

        Note: If execution times out, the worker process may still be running.
        The pool will be terminated and recreated to prevent resource leaks.

        :param js_code: JavaScript code to execute (should be a function)
        :param data: Data to pass to the JavaScript function
        :param timeout: Timeout in seconds (default: 5)
        :return: The result of the JavaScript execution as a string
        :raises TimeoutError: If execution exceeds timeout
        :raises RuntimeError: If JavaScript execution fails
        """
        if timeout is None:
            timeout = self._timeout

        try:
            # Get the process pool (creates it on first call)
            pool = self.get_pool()

            # Submit task to pool with timeout
            # Using apply_async allows us to set a timeout without blocking other requests
            async_result = pool.apply_async(
                _eval_js_worker_task,
                args=(js_code, data)
            )

            # Wait for result with timeout
            status, result = async_result.get(timeout=timeout)

            if status == 'error':
                raise RuntimeError(f"JavaScript execution failed: {result}")

            return result

        except mp.TimeoutError:
            log.error(f"JavaScript execution timed out after {timeout}s, recreating pool")

            # Terminate the pool to kill any hung workers
            # Note: pythonmonkey doesn't support execution timeouts at the eval() level,
            # so a hung worker will continue running until terminated
            if self._process_pool is not None:
                self._process_pool.terminate()
                self._process_pool = None

            raise TimeoutError(f"JavaScript execution timed out after {timeout}s")

    def shutdown(self):
        """
        Shutdown the process pool gracefully.
        Should be called during application shutdown.
        """
        if self._process_pool is not None:
            log.info("Shutting down JavaScript worker pool")
            self._process_pool.close()
            self._process_pool.join()
            self._process_pool = None
            log.info("JavaScript worker pool shutdown complete")


# Global singleton instance
_js_executor = None
_executor_lock = mp.Lock()


def get_js_executor():
    """
    Get the global JsExecutor singleton instance.

    :return: The global JsExecutor instance
    """
    global _js_executor

    if _js_executor is None:
        with _executor_lock:
            if _js_executor is None:
                _js_executor = JsExecutor()

    return _js_executor


def shutdown_js_executor():
    """
    Shutdown the global JsExecutor instance.
    Should be called during application shutdown.
    """
    global _js_executor

    if _js_executor is not None:
        _js_executor.shutdown()
        _js_executor = None
