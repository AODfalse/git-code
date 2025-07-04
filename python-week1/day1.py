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