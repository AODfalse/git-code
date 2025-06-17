import pandas as pd
import numpy as np
def my_function():
  print("Hello from a function")

def my_function():
  print("Hello from a function")

my_function()

def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")

def my_function(*kids):
  print("The youngest child is " + kids[2])

my_function("Emil", "Tobias", "Linus")

def my_function(child3, child2, child1):
  print("The youngest child is " + child3)

my_function(child1 = "Emil", child2 = "Tobias", child3 = "Linus")

def my_function(**kid):
  print("His last name is " + kid["lname"])

my_function(fname = "Tobias", lname = "Refsnes")

def my_function(country = "Norway"):
  print("I am from " + country)

my_function("Sweden")
my_function("India")
my_function()
my_function("Brazil")

def my_function(food):
  for x in food:
    print(x)

fruits = ["apple", "banana", "cherry"]

my_function(fruits)

def my_function(x):
  return 5 * x

print(my_function(3))
print(my_function(5))
print(my_function(9))

def myfunction():
  pass

def my_function(x, /):
  print(x)

my_function(3)

def my_function(x):
  print(x)

my_function(x = 3)

def my_function(*, x):
  print(x)

my_function(x = 3)

def my_function(x):
  print(x)

my_function(3)

def my_function(a, b, /, *, c, d):
  print(a + b + c + d)

my_function(5, 6, c = 7, d = 8)

def tri_recursion(k):
  if(k > 0):
    result = k + tri_recursion(k - 1)
    print(result)
  else:
    result = 0
  return result

print("Recursion Example Results:")
tri_recursion(6)

def calculate_circle_area(r):  
    pi = 3.14
    area = pi * r ** 2         
    return area                  
assert calculate_circle_area(5) == 78.5, "面积计算错误！"
print(calculate_circle_area(5))

s = pd.Series([1, 3, 5, np.nan, 6, 8])

print(s)

dates = pd.date_range("20130101", periods=6)
print(dates)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
print(df)

df2 = pd.DataFrame(
    {
        "A": 1.0,
        "B": pd.Timestamp("20130102"),
        "C": pd.Series(1, index=list(range(4)), dtype="float32"),
        "D": np.array([3] * 4, dtype="int32"),
        "E": pd.Categorical(["test", "train", "test", "train"]),
        "F": "foo",
    }
)
print("1111")
print(df2)
print("2222")
df2.dtypes
print("3333")
print(df2.head())
print("4444")
print(df2.tail(3))
print("5555")
print(df.index)
print("6666")
print(df.columns)
print("7777")
print(df.to_numpy())
print("8888")
print(df.describe())
print("9999")
print(df.T)
print("101010")
print(df.sort_index(axis=1, ascending=False))
print("111111")
print(df.sort_values(by="B"))
print("121212")
print(df["A"])  # 访问单列
print("131313")
print(df[0:3])  # 访问前3行
print("141414")
print(df["20130102":"20130104"])  # 通过日期范围访问
print("151515")
print(df.loc[dates[0]])  # 通过标签访问
print("161616")
print(df.iloc[3])  # 通过位置访问
print("171717")
print(df.iloc[3:5, 0:2])  # 通过位置访问
print("181818")
print(df[df["A"] > 0])  # 条件筛选
print("191919")
df2 = df.copy()
df2["E"] = ["one", "one", "two", "three", "four", "three"]
print("202020")
print(df2[df2["E"].isin(["two", "four"])])  # 筛选特定类别
print("212121")
print(df.apply(np.cumsum))  # 应用函数
print("222222")
print(df.apply(lambda x: x.max() - x.min()))  # 应用自定义函数
print("232323")
print(df.apply(lambda x: x.max() - x.min(), axis=1))  # 按行应用函数
print("242424")
print(df.apply(lambda x: x.max() - x.min(), axis=0))  # 按列应用函数





