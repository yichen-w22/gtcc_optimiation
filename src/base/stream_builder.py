"""按字典定义构建汽水和气体流股，输入使用 SI 单位。"""

from ..working_fluid.gas import GasComposition, GasState
from ..working_fluid.steam_water import WaterSteamState


def build_stream(name, definitions, row, ref_env):
    """字符串参数从 row 读取，常量直接使用；成分字典使用摩尔分数。"""
    build_methods = {
        "WaterSteamState": {
            "from_PT": WaterSteamState.from_PT,
            "from_Px": WaterSteamState.from_Px,
            "from_Ph": WaterSteamState.from_Ph,
            "from_Ps": WaterSteamState.from_Ps,
        },
        "GasState": {
            "from_TP": GasState.from_TP,
            "from_Ph": GasState.from_Ph,
            "from_Ps": GasState.from_Ps,
        },
    }

    definition = definitions[name]
    parameters = {}

    for parameter, source in definition.items():
        if parameter in ("type", "method", "note"):
            continue

        if isinstance(source, str):
            parameters[parameter] = row.get(source)
        else:
            parameters[parameter] = source

    stream_type = definition.get("type", "WaterSteamState")
    if stream_type == "GasState":
        composition = parameters.get("composition")
        if isinstance(composition, dict):
            composition = GasComposition.from_dict(composition)
        elif composition is not None and not isinstance(composition, GasComposition):
            raise TypeError(f"流股 {name} 的 composition 必须是 GasComposition、字典或 None")
        parameters["composition"] = composition

    constructor = build_methods[stream_type][definition["method"]]
    stream = constructor(name=name, ref=ref_env, **parameters)

    return stream


def build_streams(names, definitions, row, ref_env):
    """按需构建流股，返回以流股名称为键的字典。"""
    streams = {}

    for name in names:
        stream = build_stream(name, definitions, row, ref_env)
        streams[stream.name] = stream

    return streams
