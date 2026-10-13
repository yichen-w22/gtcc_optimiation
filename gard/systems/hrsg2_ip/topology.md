```mermaid
flowchart TB
    %% 设备与组合节点；组节点保留 1～2 级再热受热面的整体连接
    ip2_pump_split["中压给水泵入口分流"]
    ip2_pump1["中压给水泵 1"]
    ip2_pump2["中压给水泵 2"]
    ip2_pump_merge["中压给水泵出口汇流"]
    ip2_feed_split["中压给水与再热减温水分流"]
    ip2_economizer["中压省煤器"]
    ip2_drum_evaporator["中压汽包"]
    ip2_superheater["中压过热器"]
    ip2_fresh_steam_mix["中压新蒸汽与冷再热蒸汽混合"]
    ip2_reheater_group["再热器组（1～2）"]
    ip2_attemperator["再热减温器"]
    ip2_reheater3["再热器 3"]

    %% 外部接口；圆角节点表示本系统的入口和出口
    ip2_feedwater_in(["来自 2 号炉低压汽包"])
    ip2_cold_reheat_in(["来自汽轮机高压缸"])
    ip2_hot_reheat_out(["去往汽轮机中压缸"])

    %% 物质流连接；流股按设备位置和介质命名
    ip2_feedwater_in -->|2号炉中压给水泵入口母管| ip2_pump_split
    ip2_pump_split -->|2号炉中压给水泵1入口| ip2_pump1
    ip2_pump_split -->|2号炉中压给水泵2入口| ip2_pump2
    ip2_pump1 -->|2号炉中压给水泵1出口| ip2_pump_merge
    ip2_pump2 -->|2号炉中压给水泵2出口| ip2_pump_merge
    ip2_pump_merge -->|2号炉中压给水泵出口母管| ip2_feed_split
    ip2_feed_split -->|2号炉中压给水| ip2_economizer
    ip2_feed_split -->|2号炉再热减温水| ip2_attemperator
    ip2_economizer -->|2号炉中压汽包入口| ip2_drum_evaporator
    ip2_drum_evaporator -->|2号炉中压汽包饱和蒸汽| ip2_superheater
    ip2_superheater -->|2号炉中压新蒸汽| ip2_fresh_steam_mix
    ip2_cold_reheat_in -->|2号炉冷再热蒸汽| ip2_fresh_steam_mix
    ip2_fresh_steam_mix -->|2号炉再热器入口混合蒸汽| ip2_reheater_group
    ip2_reheater_group -->|2号炉再热减温前蒸汽| ip2_attemperator
    ip2_attemperator -->|2号炉再热减温后蒸汽| ip2_reheater3
    ip2_reheater3 -->|2号炉热再热蒸汽| ip2_hot_reheat_out

    classDef boundary fill:#eef5ff,stroke:#526d82,stroke-dasharray:5 5,color:#162b3b;
    class ip2_feedwater_in,ip2_cold_reheat_in,ip2_hot_reheat_out boundary;
```
