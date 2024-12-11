import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.gridspec import GridSpec
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import glob
import re
import os

def load_and_process_data():
    # [保持原有的数据加载代码不变]
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
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

def create_radar_chart(df):
    """创建雷达图比较不同组别的任务分配"""
    # 计算各组的平均值
    metrics = ['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']
    avg_by_group = df.groupby(['Group_Type', 'Gender'])[metrics].mean()
    
    # 创建雷达图
    fig = go.Figure()
    
    # 定义每个组的颜色和线型
    colors = {'Experimental': 'rgb(31, 119, 180)', 'Control': 'rgb(255, 127, 14)'}
    line_dash = {'Male': 'solid', 'Female': 'dash'}
    
    for group in ['Experimental', 'Control']:
        for gender in ['Male', 'Female']:
            values = avg_by_group.loc[(group, gender)].values.tolist()
            values.append(values[0])  # 闭合雷达图
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics + [metrics[0]],
                name=f'{gender} ({group})',
                line=dict(color=colors[group], dash=line_dash[gender]),
                fill='tonext' if gender == 'Male' else None,
                opacity=0.6
            ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title='Task Distribution Radar Chart'
    )
    fig.write_html("radar_chart.html")

def create_3d_scatter(df):
    """创建3D散点图展示三种任务的关系"""
    fig = go.Figure()
    
    for group in ['Experimental', 'Control']:
        for gender in ['Male', 'Female']:
            mask = (df['Group_Type'] == group) & (df['Gender'] == gender)
            
            fig.add_trace(go.Scatter3d(
                x=df[mask]['Low_Value_Tasks'],
                y=df[mask]['High_Value_Tasks'],
                z=df[mask]['Leadership_Tasks'],
                mode='markers',
                name=f'{gender} ({group})',
                marker=dict(size=5),
                text=df[mask]['Year'].astype(str) + ' Year'
            ))
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Low Value Tasks',
            yaxis_title='High Value Tasks',
            zaxis_title='Leadership Tasks'
        ),
        title='3D Task Distribution'
    )
    fig.write_html("3d_scatter.html")

def create_sunburst(df):
    """创建旭日图展示任务层级分布"""
    # 计算平均值并规范化数据
    sunburst_data = df.groupby(['Group_Type', 'Gender', 'Year'])[
        ['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks']
    ].mean().reset_index()
    
    fig = px.sunburst(
        sunburst_data,
        path=['Group_Type', 'Gender', 'Year'],
        values='Leadership_Tasks',
        color='High_Value_Tasks',
        hover_data=['Low_Value_Tasks', 'High_Value_Tasks', 'Leadership_Tasks'],
        title='Task Hierarchy Analysis'
    )
    fig.write_html("sunburst.html")

def create_parallel_coordinates(df):
    """创建平行坐标图展示多维度关系"""
    fig = go.Figure(data=
        go.Parcoords(
            line=dict(
                color=df['Year'],
                colorscale='Viridis',
            ),
            dimensions=list([
                dict(range=[0, 5],
                     label='Low Value Tasks',
                     values=df['Low_Value_Tasks']),
                dict(range=[0, 5],
                     label='High Value Tasks',
                     values=df['High_Value_Tasks']),
                dict(range=[0, 5],
                     label='Leadership Tasks',
                     values=df['Leadership_Tasks']),
                dict(range=[0, 10],
                     label='Year',
                     values=df['Year'])
            ])
        )
    )
    fig.update_layout(title='Parallel Coordinates Plot of Tasks')
    fig.write_html("parallel_coordinates.html")

def create_animated_bubble(df):
    """创建动画气泡图展示时间变化"""
    fig = px.scatter(
        df,
        x='High_Value_Tasks',
        y='Leadership_Tasks',
        size='Low_Value_Tasks',
        color='Gender',
        facet_col='Group_Type',
        animation_frame='Year',
        hover_name='Department',
        size_max=20,
        title='Task Distribution Evolution'
    )
    fig.write_html("animated_bubble.html")

def analyze_gender_differences():
    # 加载数据
    df = load_and_process_data()
    
    # 创建高级可视化
    create_radar_chart(df)
    create_3d_scatter(df)
    create_sunburst(df)
    create_parallel_coordinates(df)
    create_animated_bubble(df)
    
    # [保留原有的统计分析代码]
    summary = df.groupby(['Group_Type', 'Gender']).agg({
        'Low_Value_Tasks': ['mean', 'std'],
        'High_Value_Tasks': ['mean', 'std'],
        'Leadership_Tasks': ['mean', 'std']
    }).round(2)
    
    return df, summary

if __name__ == "__main__":
    try:
        data, summary = analyze_gender_differences()
        
        print("\nAnalysis completed successfully!")
        print("The following interactive visualization files have been generated:")
        print("1. radar_chart.html - Task distribution radar chart")
        print("2. 3d_scatter.html - 3D visualization of task relationships")
        print("3. sunburst.html - Hierarchical task distribution")
        print("4. parallel_coordinates.html - Multi-dimensional task relationships")
        print("5. animated_bubble.html - Animated task distribution over time")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")