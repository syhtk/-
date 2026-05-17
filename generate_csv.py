import pandas as pd
from mock_review_generator import generate_mock_reviews

# 我们生成包含 10 个核心大品类的混合数据集，每个品类生成 200 条数据，总共 2000 条
categories = [
    "智能手机", "女装连衣裙", "零食大礼包", "洗面奶", "智能耳机", 
    "扫地机器人", "运动跑鞋", "保温杯", "猫粮", "机械键盘"  # 未配置专门模板的将会使用强大的“兜底通用生成”
]

all_dfs = []

for cat in categories:
    print(f"正在生成 {cat} 的模拟数据...")
    df = generate_mock_reviews(cat, 200) # 每个品类 200 条
    all_dfs.append(df)

# 合并所有数据
final_df = pd.concat(all_dfs, ignore_index=True)

# 随机打乱顺序，使得训练数据分布均匀
final_df = final_df.sample(frac=1).reset_index(drop=True)

# 保存为 CSV 文件
output_file = "raw_comments.csv"
final_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"\n✅ 成功生成 {len(final_df)} 条跨品类电商评论测试数据！")
print(f"文件已覆盖保存至: {output_file}")

