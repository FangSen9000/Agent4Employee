import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 读取数据
female_file_path = 'female_salary.csv'  # 替换为实际路径
male_file_path = 'male_salary.csv'  # 替换为实际路径

# 添加列名
columns = ['Name', 'Gender', 'Department', 'Age', 'Position', 'Starting Salary',
           'age 24', 'age 26', 'age 28', 'age 30', 'age 32']

# 读取数据
female_data = pd.read_csv(female_file_path, names=columns, header=0)
male_data = pd.read_csv(male_file_path, names=columns, header=0)

# 2. 数据合并与处理
female_data['Gender'] = 'Female'
male_data['Gender'] = 'Male'
combined_data = pd.concat([female_data, male_data], ignore_index=True)

# 计算总增长
combined_data['Total Growth'] = combined_data['age 32'] - combined_data['Starting Salary']

# 按不同维度生成分析结果
# 平均工资增长按性别
avg_growth_by_gender = combined_data.groupby('Gender')['Total Growth'].mean()

# 平均工资增长按部门
avg_growth_by_department = combined_data.groupby(['Department', 'Gender'])['Total Growth'].mean().unstack()

# 平均工资增长按起薪范围
combined_data['Starting Salary Range'] = pd.cut(
    combined_data['Starting Salary'], bins=[0, 2000, 4000, 6000, 8000, 10000, 12000]
)
avg_growth_by_salary_range = combined_data.groupby(['Starting Salary Range', 'Gender'])['Total Growth'].mean().unstack()

# 工资增长分布按性别
growth_distribution = combined_data.groupby('Gender')['Total Growth'].describe()

# 工资增长按年龄段
growth_by_age = combined_data.groupby('Gender')[['age 24', 'age 26', 'age 28', 'age 30', 'age 32']].mean()

# 3. 图表生成与保存

# (1) 平均工资增长按性别
plt.figure(figsize=(6, 4))
avg_growth_by_gender.plot(kind='bar', color=['blue', 'orange'], legend=False)
plt.title("Average Salary Growth by Gender")
plt.ylabel("Average Growth")
plt.xlabel("Gender")
plt.tight_layout()
plt.savefig('avg_growth_by_gender.png')

# (2) 平均工资增长按部门
plt.figure(figsize=(8, 6))
avg_growth_by_department.plot(kind='bar', figsize=(8, 6))
plt.title("Average Salary Growth by Department and Gender")
plt.ylabel("Average Growth")
plt.xlabel("Department")
plt.tight_layout()
plt.savefig('avg_growth_by_department.png')

# (3) 平均工资增长按起薪范围
plt.figure(figsize=(8, 6))
avg_growth_by_salary_range.plot(kind='bar', figsize=(8, 6))
plt.title("Average Salary Growth by Starting Salary Range and Gender")
plt.ylabel("Average Growth")
plt.xlabel("Starting Salary Range")
plt.tight_layout()
plt.savefig('avg_growth_by_salary_range.png')

# (4) 工资增长分布按性别
plt.figure(figsize=(8, 6))
growth_distribution[['mean', 'std']].plot(kind='bar', yerr='std', legend=True)
plt.title("Salary Growth Distribution by Gender")
plt.ylabel("Growth")
plt.xlabel("Gender")
plt.tight_layout()
plt.savefig('growth_distribution_by_gender.png')

# (5) 工资增长按年龄段
plt.figure(figsize=(10, 6))
growth_by_age.T.plot(kind='line', figsize=(10, 6))
plt.title("Salary Growth by Age Intervals and Gender")
plt.ylabel("Average Salary")
plt.xlabel("Age Intervals")
plt.tight_layout()
plt.savefig('growth_by_age_intervals.png')

print("All figures have been successfully saved.")

# 计算每个年龄段的薪资增长
combined_data['Growth 24'] = combined_data['age 24'] - combined_data['Starting Salary']
combined_data['Growth 26'] = combined_data['age 26'] - combined_data['Starting Salary']
combined_data['Growth 28'] = combined_data['age 28'] - combined_data['Starting Salary']
combined_data['Growth 30'] = combined_data['age 30'] - combined_data['Starting Salary']
combined_data['Growth 32'] = combined_data['age 32'] - combined_data['Starting Salary']

# 为了绘图方便，重塑数据，将其变为长格式
melted_data = pd.melt(combined_data, id_vars=['Gender'], value_vars=['Growth 24', 'Growth 26', 'Growth 28', 'Growth 30', 'Growth 32'],
                      var_name='Age Interval', value_name='Salary Growth')

# 绘制箱形图
plt.figure(figsize=(10, 6))
ax = sns.boxplot(x='Age Interval', y='Salary Growth', hue='Gender', data=melted_data)
plt.title("Conditional Salary Growth Distribution by Gender Over Two-Year Intervals")
plt.ylabel("Salary Growth")
plt.xlabel("Age Interval")
plt.legend(title='Gender')
plt.tight_layout()
plt.savefig('conditional_salary_growth_by_gender.png')
plt.show()

print("The conditional salary growth distribution chart has been successfully saved.")