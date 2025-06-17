import pandas as pd

# 创建电影评分字典
movie_ratings = {
    "肖申克的救赎": 9.7,
    "阿甘正传": 9.5,
    "泰坦尼克号": 9.4,
    "盗梦空间": 9.3,
    "星际穿越": 9.3
}

# 打印字典验证
print("我的电影评分字典：")
print(movie_ratings)

# 添加新电影
movie_ratings["千与千寻"] = 9.4
print("\n添加新电影后的字典：")
print(movie_ratings)

# 访问特定电影评分
target_movie = "肖申克的救赎"
print(f"\n{target_movie}的评分是：{movie_ratings[target_movie]}")

# 挑战1：计算平均评分
ratings = list(movie_ratings.values())
average = sum(ratings) / len(ratings)
print(f"\n平均评分：{average:.2f}")

# 挑战2：找出最高分电影
max_movie = max(movie_ratings, key=movie_ratings.get)
print(f"最高分电影：{max_movie} ({movie_ratings[max_movie]})")


def save_movie_data(ratings_dict):
    """
    将电影评分字典保存到CSV文件
    """
    df = pd.DataFrame(list(ratings_dict.items()), columns=['片名', '评分'])
    df['评分'] = df['评分'].astype(float)
    df.to_csv('movies.csv', index=False)
    print("电影数据已保存到 movies.csv")


save_movie_data(movie_ratings)


def load_and_query():
    """
    从CSV文件加载电影数据并查询特定电影的评分
    """
    try:
        # 加载CSV文件
        df = pd.read_csv('movies.csv')
        
        # 查询包含"肖申克"的电影
        query_result = df[df['片名'].str.contains("肖申克")]
        
        # 检查是否找到结果
        if not query_result.empty:
            score = query_result.iloc[0]['评分']
            print(f"肖申克评分：{score}")
        else:
            print("未找到包含'肖申克'的电影")
    except FileNotFoundError:
        print("错误：未找到movies.csv文件，请先运行save_movie_data函数")
    except Exception as e:
        print(f"发生未知错误：{e}")


load_and_query()