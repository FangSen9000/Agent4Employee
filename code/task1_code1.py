import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
import os

def load_and_process_data():
    # 打印当前工作目录
    print("Current working directory:", os.getcwd())
    
    # 创建空列表存储所有数据
    all_data = []
    
    # 使用glob获取所有csv文件
    files = glob.glob("*.csv")
    print(f"Found {len(files)} CSV files:")
    for file in files:
        print(f"- {file}")
    
    if not files:
        raise ValueError("No CSV files found in the current directory!")
    
    for file in files:
        try:
            # 读取CSV文件
            df = pd.read_csv(file, encoding='utf-8')
            print(f"\nProcessing file: {file}")
            
            # 从文件名提取信息
            if "对照组" in file:
                group_type = "Control"
                gender = "Male" if "S_" in file else "Female"
            else:
                group_type = "Experimental"
                gender = "Male" if "男" in file else "Female"
            
            # 提取年份
            year = re.search(r'第(\d+)年', file).group(1)
            print(f"- Group Type: {group_type}")
            print(f"- Gender: {gender}")
            print(f"- Year: {year}")
            print(f"- Successfully loaded {len(df)} rows")
            
            # 添加额外信息到数据框
            df['Year'] = int(year)
            df['Group_Type'] = group_type
            df['Gender'] = gender
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    if not all_data:
        raise ValueError("No data was successfully loaded from the CSV files!")
    
    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal combined data shape: {combined_df.shape}")
    
    return combined_df

def plot_metrics_over_time(df, metric, title):
    plt.figure(figsize=(12, 6))
    
    # 为实验组和对照组分别绘制线条
    for group_type in ['Experimental', 'Control']:
        for gender in ['Male', 'Female']:
            data = df[
                (df['Group_Type'] == group_type) & 
                (df['Gender'] == gender)
            ].groupby('Year')[metric].mean()
            
            style = '-' if group_type == 'Experimental' else '--'
            plt.plot(data.index, data.values, 
                    marker='o' if group_type == 'Experimental' else 's',
                    linestyle=style,
                    label=f'{gender} ({group_type})')
    
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(metric)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{metric}_analysis.png")
    plt.close()

def analyze_performance(df):
    plt.figure(figsize=(15, 6))
    
    # 分别为实验组和对照组创建子图
    for i, group_type in enumerate(['Experimental', 'Control'], 1):
        plt.subplot(1, 2, i)
        
        # 计算每个性别、年份组合的绩效分布
        performance_data = df[df['Group_Type'] == group_type].pivot_table(
            index=['Gender', 'Year'],
            columns='Performance',
            aggfunc='size',
            fill_value=0
        )
        
        # 转换为百分比
        performance_data = performance_data.div(performance_data.sum(axis=1), axis=0) * 100
        
        # 绘制堆叠柱状图
        performance_data.plot(kind='bar', stacked=True)
        plt.title(f'{group_type} Group Performance Distribution')
        plt.xlabel('Gender and Year')
        plt.ylabel('Percentage')
        plt.legend(title='Performance Grade')
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig("performance_distribution.png")
    plt.close()

def analyze_gender_differences():
    # 加载数据
    df = load_and_process_data()
    
    # 打印数据基本信息
    print("\nDataset Overview:")
    print(df.info())
    print("\nSample of the data:")
    print(df.head())
    
    # 分析不同指标
    metrics = [
        ('Low_Value_Tasks', 'Low Value Tasks Over Time'),
        ('High_Value_Tasks', 'High Value Tasks Over Time'),
        ('Leadership_Tasks', 'Leadership Tasks Over Time')
    ]
    
    for metric, title in metrics:
        plot_metrics_over_time(df, metric, title)
    
    # 分析绩效分布
    analyze_performance(df)
    
    # 计算统计摘要
    summary = df.groupby(['Group_Type', 'Gender']).agg({
        'Low_Value_Tasks': ['mean', 'std'],
        'High_Value_Tasks': ['mean', 'std'],
        'Leadership_Tasks': ['mean', 'std']
    })
    
    return df, summary

if __name__ == "__main__":
    try:
        data, summary = analyze_gender_differences()
        print("\nStatistical Summary by Group Type and Gender:")
        print(summary)
        
        # 输出更详细的分析
        print("\nAverage metrics by group and gender:")
        metrics = ['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']
        for metric in metrics:
            print(f"\n{metric} analysis:")
            print(data.groupby(['Group_Type', 'Gender'])[metric].mean().round(2))
        
        print("\nAnalysis completed successfully!")
        print("Graphs have been saved as PNG files in the current directory.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")