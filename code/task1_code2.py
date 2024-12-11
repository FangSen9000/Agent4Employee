import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
import os

# Set global font sizes
plt.rcParams['font.size'] = 14  # Default font size
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.titlesize'] = 18

def load_and_process_data():
    # 创建空列表存储所有数据
    all_data = []
    
    # 使用glob获取所有csv文件
    files = glob.glob("*.csv")
    
    for file in files:
        try:
            # 读取CSV文件
            df = pd.read_csv(file, encoding='utf-8')
            
            # 从文件名提取信息
            if "对照组" in file:
                group_type = "Control"
                gender = "Male" if "S_" in file else "Female"
            else:
                group_type = "Experimental"
                gender = "Male" if "男" in file else "Female"
            
            # 提取年份
            year = re.search(r'第(\d+)年', file).group(1)
            
            # 添加额外信息到数据框
            df['Year'] = int(year)
            df['Group_Type'] = group_type
            df['Gender'] = gender
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

def plot_performance_mirror(df):
    """创建镜像条形图来展示性别性能差异"""
    plt.figure(figsize=(15, 10))
    
    # 分别处理实验组和对照组
    for i, group_type in enumerate(['Experimental', 'Control']):
        plt.subplot(2, 1, i+1)
        
        # 获取该组的数据
        group_data = df[df['Group_Type'] == group_type]
        
        # 计算每个性别-年份组合的性能分布
        male_data = group_data[group_data['Gender'] == 'Male'].groupby(['Year', 'Performance']).size().unstack(fill_value=0)
        female_data = group_data[group_data['Gender'] == 'Female'].groupby(['Year', 'Performance']).size().unstack(fill_value=0)
        
        # 转换为百分比
        male_pct = male_data.div(male_data.sum(axis=1), axis=0) * 100
        female_pct = female_data.div(female_data.sum(axis=1), axis=0) * 100
        
        # 创建镜像条形图
        years = male_pct.index
        
        # 设置颜色映射
        colors = plt.cm.Set3(np.linspace(0, 1, len(male_pct.columns)))
        
        # 绘制男性数据（上半部分）
        for j, (grade, color) in enumerate(zip(male_pct.columns, colors)):
            plt.bar(years, male_pct[grade], bottom=male_pct.iloc[:, :j].sum(axis=1),
                   label=f'Male - Grade {grade}', color=color, alpha=0.7)
        
        # 绘制女性数据（下半部分，负值）
        for j, (grade, color) in enumerate(zip(female_pct.columns, colors)):
            plt.bar(years, -female_pct[grade], bottom=-female_pct.iloc[:, :j].sum(axis=1),
                   label=f'Female - Grade {grade}', color=color, alpha=0.7)
        
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.title(f'{group_type} Group Performance Distribution', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Percentage', fontsize=14)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tick_params(labelsize=12)
    
    plt.tight_layout()
    plt.savefig("performance_mirror_distribution.png", bbox_inches='tight', dpi=300)
    plt.close()

def plot_task_distribution(df):
    """创建任务分配的箱线图"""
    fig, axes = plt.subplots(3, 1, figsize=(15, 15))
    tasks = ['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']
    
    for i, task in enumerate(tasks):
        # 为实验组和对照组分别创建箱线图
        sns.boxplot(data=df[df['Group_Type'] == 'Experimental'], 
                   x='Year', y=task, hue='Gender', 
                   ax=axes[i], palette='Set2',
                   showfliers=True)
        
        axes[i].set_title(f'{task.replace("_", " ")} Distribution (Experimental Group)', fontsize=16)
        axes[i].grid(True, alpha=0.3)
        axes[i].set_ylabel(task.replace('_', ' '), fontsize=14)
        axes[i].set_xlabel('Year', fontsize=14)
        axes[i].tick_params(labelsize=12)
        axes[i].legend(fontsize=12)
        
        # 添加均值点
        sns.pointplot(data=df[df['Group_Type'] == 'Experimental'],
                     x='Year', y=task, hue='Gender',
                     ax=axes[i], markers=['o', 's'],
                     linestyles=['-', '--'],
                     color='black', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig("task_distribution_boxplots.png", dpi=300)
    plt.close()

def plot_task_trends(df):
    """创建任务分配趋势图"""
    tasks = ['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']
    fig, axes = plt.subplots(len(tasks), 1, figsize=(15, 15))
    
    for i, task in enumerate(tasks):
        for group in ['Experimental', 'Control']:
            group_data = df[df['Group_Type'] == group]
            
            for gender in ['Male', 'Female']:
                data = group_data[group_data['Gender'] == gender]
                
                # 计算均值和标准误差
                mean = data.groupby('Year')[task].mean()
                sem = data.groupby('Year')[task].sem()
                
                # 绘制带有误差范围的趋势线
                line_style = '-' if group == 'Experimental' else '--'
                axes[i].plot(mean.index, mean.values, 
                           label=f'{gender} ({group})',
                           linestyle=line_style)
                axes[i].fill_between(mean.index, 
                                   mean.values - sem.values,
                                   mean.values + sem.values,
                                   alpha=0.2)
        
        axes[i].set_title(f'{task.replace("_", " ")} Over Time', fontsize=16)
        axes[i].set_xlabel('Year', fontsize=14)
        axes[i].set_ylabel('Average Tasks', fontsize=14)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend(fontsize=12)
        axes[i].tick_params(labelsize=12)
    
    plt.tight_layout()
    plt.savefig("task_trends.png", dpi=300)
    plt.close()

def analyze_gender_differences():
    # 加载数据
    df = load_and_process_data()
    
    # 创建可视化
    plot_performance_mirror(df)
    plot_task_distribution(df)
    plot_task_trends(df)
    
    # 计算统计摘要
    summary = df.groupby(['Group_Type', 'Gender']).agg({
        'Low_Value_Tasks': ['mean', 'std'],
        'High_Value_Tasks': ['mean', 'std'],
        'Leadership_Tasks': ['mean', 'std']
    }).round(2)
    
    # 计算实验组和对照组之间的差异
    exp_control_diff = df.groupby(['Gender', 'Year']).apply(
        lambda x: x[x['Group_Type'] == 'Experimental'][['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']].mean() - 
                 x[x['Group_Type'] == 'Control'][['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']].mean()
    ).round(2)
    
    return df, summary, exp_control_diff

if __name__ == "__main__":
    try:
        import numpy as np
        data, summary, exp_control_diff = analyze_gender_differences()
        
        print("\nStatistical Summary by Group Type and Gender:")
        print(summary)
        
        print("\nExperimental vs Control Group Differences by Gender and Year:")
        print("(Positive values indicate higher in Experimental Group)")
        print(exp_control_diff)
        
        print("\nAnalysis completed successfully!")
        print("The following visualization files have been generated:")
        print("1. performance_mirror_distribution.png - Mirror bar chart showing performance distribution")
        print("2. task_distribution_boxplots.png - Box plots showing task distribution")
        print("3. task_trends.png - Trends of task allocation over time")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")