# app/sandbox.py
import pandas as pd
import json
import io
import contextlib
import numpy as np


class PythonSandbox:
    def __init__(self):
        # 预加载常用库
        self.default_env = {
            "pd": pd,
            "np": np,
            "json": json
        }

    def _sanitize(self, obj):
        """清洗数据类型，确保 JSON 可序列化"""
        if isinstance(obj,
                      (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32,
                       np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize(i) for i in obj]
        return obj

    def execute(self, code: str, data_context: list = None) -> dict:
        """执行代码，支持注入 df 变量"""
        # 1. 静态安全检查
        if any(kw in code for kw in ["os.system", "subprocess", "eval(", "open("]):
            return {"success": False, "error": "System Policy Violation: Unsafe operations."}

        # 2. 环境注入
        local_scope = self.default_env.copy()
        if data_context:
            try:
                local_scope["df"] = pd.DataFrame(data_context)
                local_scope["data"] = data_context
            except Exception as e:
                return {"success": False, "error": f"DataFrame conversion failed: {str(e)}"}

        # 3. 捕获输出并执行
        output_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(output_capture):
                exec(code, {}, local_scope)

            stdout = output_capture.getvalue()
            chart_config = local_scope.get("chart_config", None)
            result = local_scope.get("result", None)

            return {
                "success": True,
                "stdout": stdout.strip(),
                "chart_config": self._sanitize(chart_config) if chart_config else None,
                "result": str(self._sanitize(result)) if result is not None else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}