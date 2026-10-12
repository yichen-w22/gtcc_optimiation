"""cooling measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [], columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"]
).astype({"scale": float, "offset": float})
