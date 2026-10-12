"""heating measurement configuration."""
import pandas as pd

# 1. 原始测点和数据导入
POINT_BINDINGS = pd.DataFrame(
    [["heat.drain_return.m_dot", "GARD_00NDD80WP011BF01XQ01", "t/h", "t/h", 1 / 3.6, 0.0, None]],
    columns=["field", "code", "expected_unit", "unit", "scale", "offset", "pressure_basis"],
).astype({"scale": float, "offset": float})
