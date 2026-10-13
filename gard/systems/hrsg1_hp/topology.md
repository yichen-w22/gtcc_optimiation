```mermaid
flowchart TB
    %% 设备与组合节点；组节点保留 1～3 级受热面的整体连接
    hp1_pump_split["高压给水泵入口分流"]
    hp1_pump1["高压给水泵 1"]
    hp1_pump2["高压给水泵 2"]
    hp1_pump_merge["高压给水泵出口汇流"]
    hp1_feed_split["高压给水与减温水分流"]
    hp1_economizer_group["高压省煤器组（1～3）"]
    hp1_drum_evaporator["高压汽包"]
    hp1_superheater_group["高压过热器组（1～3）"]
    hp1_attemperator["高压减温器"]
    hp1_superheater4["高压过热器 4"]

    %% 外部接口；圆角节点表示本系统的入口和出口
    hp1_feedwater_in(["来自 1 号炉低压汽包"])
    hp1_main_steam_out(["去往汽轮机高压缸"])

    %% 物质流连接；流股按设备位置和介质命名
    hp1_feedwater_in -->|1号炉高压给水泵入口母管| hp1_pump_split
    hp1_pump_split -->|1号炉高压给水泵1入口| hp1_pump1
    hp1_pump_split -->|1号炉高压给水泵2入口| hp1_pump2
    hp1_pump1 -->|1号炉高压给水泵1出口| hp1_pump_merge
    hp1_pump2 -->|1号炉高压给水泵2出口| hp1_pump_merge
    hp1_pump_merge -->|1号炉高压给水泵出口母管| hp1_feed_split
    hp1_feed_split -->|1号炉高压给水| hp1_economizer_group
    hp1_feed_split -->|1号炉高压减温水| hp1_attemperator
    hp1_economizer_group -->|1号炉高压汽包入口| hp1_drum_evaporator
    hp1_drum_evaporator -->|1号炉高压汽包饱和蒸汽| hp1_superheater_group
    hp1_superheater_group -->|1号炉高压减温前蒸汽| hp1_attemperator
    hp1_attemperator -->|1号炉高压减温后蒸汽| hp1_superheater4
    hp1_superheater4 -->|1号炉高压主蒸汽| hp1_main_steam_out

    classDef boundary fill:#eef5ff,stroke:#526d82,stroke-dasharray:5 5,color:#162b3b;
    class hp1_feedwater_in,hp1_main_steam_out boundary;
```
