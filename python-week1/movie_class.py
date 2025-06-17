# ===== 电影档案卡类 =====
class Movie:
    # 初始化方法：创建新档案卡时填写基本信息
    def __init__(self, title, rating, director):
        """TODO 1: 设置三个属性"""
        self.title = title  # 电影片名
        self.rating = rating  # 电影评分 (0-10)
        self.director = director  # 导演姓名
    
    # 显示电影信息卡片
    def print_info(self):
        """TODO 2: 打印电影信息"""
        print(f"电影档案卡".center(30, '='))
        print(f"片名：{self.title}")
        print(f"评分：{self.rating}/10")
        print(f"导演：{self.director}")
        print("=" * 30)
    
    # 额外功能：评分升级
    def upgrade_rating(self, points):
        """TODO 3: 提升电影评分"""
        if self.rating <= 10 - points:  # 检查评分是否可提升
            self.rating += points
            print(f"{self.title} 评分已升至 {self.rating}!")
        else:
            print("评分已达上限！")

# ===== 测试代码 =====
if __name__ == "__main__":
    # 创建第一部电影档案
    movie1 = Movie("肖申克的救赎", 9.7, "Frank Darabont")
    
    # 创建第二部电影档案
    movie2 = Movie("阿甘正传", 9.5, "Robert Zemeckis")
    
    # 显示档案信息
    movie1.print_info()  # 显示第一部电影信息
    movie2.print_info()  # 显示第二部电影信息
    
    # 提升阿甘正传评分
    movie2.upgrade_rating(0.3)
    movie2.print_info()