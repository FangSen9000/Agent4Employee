import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# 创建输出目录
output_dir = Path("analysis_results")
output_dir.mkdir(exist_ok=True)

def load_data(years=[0, 2, 4, 6, 8, 10]):
    """加载所有年份的数据"""
    all_data = []
    
    for year in years:
        # 加载男性数据
        male_df = pd.read_csv(f'男_实验组_第{year}年.csv')
        male_df['Year'] = year
        male_df['Gender'] = 'Male'
        all_data.append(male_df)
        
        # 加载女性数据
        female_df = pd.read_csv(f'女_实验组_第{year}年.csv')
        female_df['Year'] = year
        female_df['Gender'] = 'Female'
        all_data.append(female_df)
    
    return pd.concat(all_data, ignore_index=True)

def analyze_overall_salary_growth(data):
    """分析整体薪资增长趋势"""
    plt.figure(figsize=(12, 6))
    
    # 计算每个年份和性别的平均薪资
    salary_trends = data.groupby(['Year', 'Gender'])['Starting_Salary'].mean().unstack()
    
    # 绘制趋势线
    for gender in ['Male', 'Female']:
        plt.plot(salary_trends.index, salary_trends[gender], 
                marker='o', label=gender, linewidth=2)
        
        # 添加数据标签
        for year in salary_trends.index:
            plt.annotate(f'{salary_trends[gender][year]:,.0f}',
                        (year, salary_trends[gender][year]),
                        textcoords="offset points",
                        xytext=(0,10), ha='center')
    
    plt.title('Average Salary Progression by Gender', pad=20, fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average Salary', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks([0, 2, 4, 6, 8, 10])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'overall_salary_growth.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_department_salary(data):
    """分析各部门薪资情况"""
    plt.figure(figsize=(15, 8))
    
    # 获取主要部门（按人数排序前8个）
    main_departments = data.groupby('Department').size().nlargest(8).index
    dept_data = data[data['Department'].isin(main_departments)]
    
    # 计算各部门在不同年份的平均薪资
    dept_salary = dept_data.pivot_table(
        values='Starting_Salary',
        index='Year',
        columns='Department',
        aggfunc='mean'
    )
    
    # 绘制趋势线
    for dept in dept_salary.columns:
        plt.plot(dept_salary.index, dept_salary[dept], 
                marker='o', label=dept, linewidth=2)
    
    plt.title('Salary Trends by Department', pad=20, fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average Salary', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks([0, 2, 4, 6, 8, 10])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'department_salary_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_position_salary(data):
    """分析职位等级薪资变化"""
    plt.figure(figsize=(12, 8))
    
    # 计算各职位等级的平均薪资
    position_salary = data.pivot_table(
        values='Starting_Salary',
        index='Year',
        columns='Position',
        aggfunc='mean'
    )
    
    # 创建热力图
    sns.heatmap(position_salary, 
                annot=True, 
                fmt=',.0f',
                cmap='YlOrRd',
                cbar_kws={'label': 'Average Salary'})
    
    plt.title('Salary by Position Level Over Time', pad=20, fontsize=14)
    plt.xlabel('Position Level', fontsize=12)
    plt.ylabel('Year', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'position_salary_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_salary_distribution(data):
    """分析薪资分布情况"""
    plt.figure(figsize=(15, 6))
    
    # 创建箱线图
    sns.boxplot(x='Year', y='Starting_Salary', hue='Gender', data=data)
    
    plt.title('Salary Distribution by Year and Gender', pad=20, fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Salary', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'salary_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def calculate_growth_rates(data):
    """计算各种增长率并生成报告"""
    # 计算总体增长率
    summary = pd.DataFrame()
    
    for gender in ['Male', 'Female']:
        gender_data = data[data['Gender'] == gender]
        start_salary = gender_data[gender_data['Year'] == 0]['Starting_Salary'].mean()
        end_salary = gender_data[gender_data['Year'] == 10]['Starting_Salary'].mean()
        total_growth = (end_salary / start_salary - 1) * 100
        annual_growth = (((end_salary / start_salary) ** (1/5)) - 1) * 100
        
        summary.loc[gender, 'Total Growth (%)'] = total_growth
        summary.loc[gender, 'Annual Growth (%)'] = annual_growth
    
    # 保存增长率报告
    summary.round(2).to_csv(output_dir / 'growth_rates_summary.csv')
    
    return summary

def main():
    print("Starting analysis...")
    
    # 加载数据
    data = load_data()
    
    # 执行各项分析
    print("1. Analyzing overall salary growth...")
    analyze_overall_salary_growth(data)
    
    print("2. Analyzing department salary trends...")
    analyze_department_salary(data)
    
    print("3. Analyzing position-based salary...")
    analyze_position_salary(data)
    
    print("4. Analyzing salary distribution...")
    analyze_salary_distribution(data)
    
    print("5. Calculating growth rates...")
    growth_summary = calculate_growth_rates(data)
    print("\nGrowth Rate Summary:")
    print(growth_summary)
    
    print(f"\nAnalysis complete! Results saved in {output_dir}")

if __name__ == "__main__":
    main()