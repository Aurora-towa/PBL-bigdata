# 心脏病与最大运动心率作业

`心脏病与最大运动心率_作业完成稿.docx` 回答工作单五项任务，内含四张原创组合图、图注及参考文献。

## 图形

- figure1_primary：疾病分组分布及 Welch 均值差与 95% CI。
- figure2_adjustment：年龄、性别、中心调整模型及各中心均值差。
- figure3_associations：年龄与心率关联、各性别疾病比例。
- figure4_prediction：折外 ROC 和校准；比较五折与留中心验证。

PNG 为 400 dpi 位图；PDF 和 SVG 为可编辑矢量容器（密集散点以栅格嵌入）。英文轴标签配中文图注，所有图由课程数据重新绘制。

## 复现

保留目录结构：项目根目录下 `data/heart-disease-hypothesis.csv` 和 `outputs/analysis.py`。

Python 3.12，安装 requirements.txt 后，在根目录运行：

```powershell
python -m pip install -r outputs/requirements.txt
python outputs/analysis.py
```

脚本将重新生成图形、统计表、results.json、折外预测和 Word 文档。固定随机种子为 20261013；不读取教师参考或 review 目录。

主要分析采用 thalach 非缺失的 865 人，不插补结局。预测使用 age、sex、thalach，在训练折内插补和标准化，不使用 num 或 disease_label。预测 AUC 的 bootstrap 区间固定折外概率，未涵盖重新训练不确定性。全部补充检验均为探索性，未校正多重比较。

Word 版式使用 Microsoft YaHei 与 Calibri；图中文字使用 Arial，其他环境字体替换可能改变分页。当前机器使用 Microsoft Word 导出预览并检查全部页面。

数据文件 SHA256：1ed78749c19deeb14d9498794d2d0e43ef0bdbea8837083c52ac5aedbb3a7298。
