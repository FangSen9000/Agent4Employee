import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import glob
import re

def load_and_process_data():
    all_data = []
    files = glob.glob("*.csv")
    
    for file in files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
            
            if "对照组" in file:
                group_type = "Control"
                gender = "Male" if "S_" in file else "Female"
            else:
                group_type = "Experimental"
                gender = "Male" if "男" in file else "Female"
            
            year = re.search(r'第(\d+)年', file).group(1)
            
            df['Year'] = int(year)
            df['Group_Type'] = group_type
            df['Gender'] = gender
            
            # 确保Performance列是字符串类型
            df['Performance'] = df['Performance'].astype(str)
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # 打印数据样本以检查格式
    print("\nData sample:")
    print(combined_df[['Gender', 'Group_Type', 'Year', 'Performance']].head())
    print("\nPerformance value counts:")
    print(combined_df['Performance'].value_counts())
    
    return combined_df

def create_interactive_performance_dashboard(df):
    """创建交互式性能评估仪表板"""
    
    # 创建两个子图：条形图和趋势图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Performance Distribution by Gender',
            'Performance Trends Over Time',
            'Performance Distribution Heatmap',
            'Performance Grade Comparison'
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "heatmap"}, {"type": "bar"}]
        ]
    )
    
    # 1. 条形图：显示性别性能分布
    for gender in ['Male', 'Female']:
        perf_dist = df[df['Gender'] == gender]['Performance'].value_counts()
        fig.add_trace(
            go.Bar(
                name=gender,
                x=list(perf_dist.index),  # 转换为列表以确保顺序
                y=list(perf_dist.values),
                text=list(perf_dist.values),
                textposition='auto',
            ),
            row=1, col=1
        )
    
    # 2. 趋势图：显示随时间变化的A级性能比例
    for gender in ['Male', 'Female']:
        for group in ['Experimental', 'Control']:
            mask = (df['Gender'] == gender) & (df['Group_Type'] == group)
            perf_trend = df[mask].groupby('Year').apply(
                lambda x: (x['Performance'] == 'A').mean() * 100
            )
            
            fig.add_trace(
                go.Scatter(
                    name=f'{gender} ({group})',
                    x=perf_trend.index,
                    y=perf_trend.values,
                    mode='lines+markers',
                ),
                row=1, col=2
            )
    
    # 3. 热力图：显示性能等级分布
    perf_heatmap = pd.crosstab(
        [df['Gender'], df['Group_Type']],
        df['Performance'],
        normalize='index'
    ) * 100
    
    fig.add_trace(
        go.Heatmap(
            z=perf_heatmap.values,
            x=perf_heatmap.columns,
            y=[f"{g} ({t})" for g, t in perf_heatmap.index],
            text=[[f"{val:.1f}%" for val in row] for row in perf_heatmap.values],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorscale="RdYlBu",
        ),
        row=2, col=1
    )
    
    # 4. 分组条形图：比较不同组别的性能
    unique_grades = sorted(df['Performance'].unique())
    for grade in unique_grades:
        grade_data = []
        labels = []
        for gender in ['Male', 'Female']:
            for group in ['Experimental', 'Control']:
                mask = (df['Gender'] == gender) & (df['Group_Type'] == group)
                percentage = (df[mask]['Performance'] == grade).mean() * 100
                grade_data.append(percentage)
                labels.append(f"{gender} ({group})")
        
        fig.add_trace(
            go.Bar(
                name=f'Grade {grade}',
                x=labels,
                y=grade_data,
                text=[f"{val:.1f}%" for val in grade_data],
                textposition='auto',
            ),
            row=2, col=2
        )
    
    # 更新布局
    fig.update_layout(
        height=900,
        width=1200,
        title_text="Interactive Performance Analysis Dashboard",
        showlegend=True,
        barmode='group',
        template='plotly_white',
        
        # 更新标题字体
        title_font=dict(size=24),
        
        # 更新子图标题字体
        font=dict(size=12),
    )
    
    # 更新x轴和y轴标签
    fig.update_xaxes(title_text="Performance Grade", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    
    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_yaxes(title_text="Percentage of Grade A (%)", row=1, col=2)
    
    fig.update_xaxes(title_text="Performance Grade", row=2, col=1)
    fig.update_yaxes(title_text="Group", row=2, col=1)
    
    fig.update_xaxes(title_text="Group", row=2, col=2)
    fig.update_yaxes(title_text="Percentage (%)", row=2, col=2)
    
    # 保存为交互式HTML文件
    fig.write_html("performance_dashboard.html")

def analyze_performance():
    # 加载数据
    df = load_and_process_data()
    
    # 打印基本统计信息
    print("\nBasic statistics:")
    for group in ['Experimental', 'Control']:
        for gender in ['Male', 'Female']:
            print(f"\n{gender} ({group}) performance distribution:")
            mask = (df['Gender'] == gender) & (df['Group_Type'] == group)
            print(df[mask]['Performance'].value_counts(normalize=True).round(3) * 100)
    
    # 创建交互式仪表板
    create_interactive_performance_dashboard(df)
    
    return df

if __name__ == "__main__":
    try:
        data = analyze_performance()
        print("\nAnalysis completed successfully!")
        print("An interactive dashboard has been generated as 'performance_dashboard.html'")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print("\nDetailed error information:")
        import traceback
        print(traceback.format_exc())