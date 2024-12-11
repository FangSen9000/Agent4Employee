import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set global style
plt.style.use('bmh')
sns.set_palette("deep")

# Create output directory
output_dir = Path("analysis_results")
output_dir.mkdir(exist_ok=True)

# Define years for consistent use across all plots
YEARS = [0, 2, 4, 6, 8, 10]
YEAR_LABELS = [f'Year {year}' for year in YEARS]

def load_data(base_years=YEARS):
    """Load and combine all CSV files"""
    male_dfs = []
    female_dfs = []
    
    for year in base_years:
        male_df = pd.read_csv(f'男_实验组_第{year}年.csv')
        male_df['Year'] = year
        male_dfs.append(male_df)
        
        female_df = pd.read_csv(f'女_实验组_第{year}年.csv')
        female_df['Year'] = year
        female_dfs.append(female_df)
    
    male_data = pd.concat(male_dfs, ignore_index=True)
    female_data = pd.concat(female_dfs, ignore_index=True)
    
    return male_data, female_data

def analyze_salary_progression(male_data, female_data):
    """Analyze salary progression trends"""
    plt.figure(figsize=(12, 8))
    
    # Calculate average salary by year and position level
    male_salary = male_data.groupby(['Year', 'Position'])['Starting_Salary'].mean().unstack()
    female_salary = female_data.groupby(['Year', 'Position'])['Starting_Salary'].mean().unstack()
    
    # Plot salary trends for each position level
    for level in range(1, 6):
        if level in male_salary.columns:
            plt.plot(YEARS, male_salary[level], 
                    marker='o', linestyle='-', label=f'Male Level {level}')
        if level in female_salary.columns:
            plt.plot(YEARS, female_salary[level], 
                    marker='s', linestyle='--', label=f'Female Level {level}')
    
    plt.title('Salary Progression by Position Level', pad=20, fontsize=14)
    plt.xlabel('Time Period', fontsize=12)
    plt.ylabel('Average Salary', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.xticks(YEARS, YEAR_LABELS)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'salary_progression.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_position_distribution(male_data, female_data):
    """Analyze position distribution"""
    # Select first and last year for comparison
    first_year = min(YEARS)
    last_year = max(YEARS)
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    
    colors = ['#2ecc71', '#e74c3c']
    
    for idx, year in enumerate([first_year, last_year]):
        male_pos = male_data[male_data['Year'] == year]['Position'].value_counts().sort_index()
        female_pos = female_data[female_data['Year'] == year]['Position'].value_counts().sort_index()
        
        # Ensure all position levels are represented
        all_positions = pd.Series(0, index=range(1, 6))
        male_pos = (male_pos.reindex(all_positions.index).fillna(0))
        female_pos = (female_pos.reindex(all_positions.index).fillna(0))
        
        x = np.arange(5)  # 5 position levels
        width = 0.35
        
        axes[idx].bar(x - width/2, male_pos, width, color=colors[0], label='Male',
                     alpha=0.8, edgecolor='white')
        axes[idx].bar(x + width/2, female_pos, width, color=colors[1], label='Female',
                     alpha=0.8, edgecolor='white')
        
        axes[idx].set_title(f'Position Distribution - Year {year}', pad=20, fontsize=12)
        axes[idx].set_xlabel('Position Level', fontsize=10)
        axes[idx].set_ylabel('Number of Employees', fontsize=10)
        axes[idx].legend()
        axes[idx].grid(True, linestyle='--', alpha=0.3)
        
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels([f'Level {i}' for i in range(1, 6)])
    
    plt.suptitle('Position Level Distribution Analysis', fontsize=14, y=1.05)
    plt.tight_layout()
    plt.savefig(output_dir / 'position_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_promotion_trajectory(male_data, female_data):
    """Analyze promotion trajectories over time"""
    plt.figure(figsize=(12, 8))
    
    # Calculate average position level by year
    male_level = male_data.groupby('Year')['Position'].mean()
    female_level = female_data.groupby('Year')['Position'].mean()
    
    plt.plot(YEARS, male_level[YEARS], marker='o', 
             linestyle='-', label='Male Average Level', color='#2ecc71')
    plt.plot(YEARS, female_level[YEARS], marker='s', 
             linestyle='-', label='Female Average Level', color='#e74c3c')
    
    plt.title('Career Progression Trajectory', pad=20, fontsize=14)
    plt.xlabel('Time Period', fontsize=12)
    plt.ylabel('Average Position Level', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.ylim(0.5, 5.5)  # Set y-axis limits to show full range of levels
    plt.xticks(YEARS, YEAR_LABELS)
    
    # Add level markers
    plt.axhline(y=1, color='gray', linestyle=':', alpha=0.3)
    plt.axhline(y=2, color='gray', linestyle=':', alpha=0.3)
    plt.axhline(y=3, color='gray', linestyle=':', alpha=0.3)
    plt.axhline(y=4, color='gray', linestyle=':', alpha=0.3)
    plt.axhline(y=5, color='gray', linestyle=':', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'promotion_trajectory.png', dpi=300, bbox_inches='tight')
    plt.close()

def analyze_salary_growth_rate(male_data, female_data):
    """Analyze salary growth rate over time"""
    plt.figure(figsize=(12, 8))
    
    # Calculate average salary by year
    male_salary = male_data.groupby('Year')['Starting_Salary'].mean()
    female_salary = female_data.groupby('Year')['Starting_Salary'].mean()
    
    # Calculate growth rate
    male_growth = male_salary.pct_change()
    female_growth = female_salary.pct_change()
    
    plt.plot(YEARS[1:], male_growth[YEARS[1:]] * 100, marker='o',
             linestyle='-', label='Male Salary Growth', color='#2ecc71')
    plt.plot(YEARS[1:], female_growth[YEARS[1:]] * 100, marker='s',
             linestyle='-', label='Female Salary Growth', color='#e74c3c')
    
    plt.title('Salary Growth Rate Over Time', pad=20, fontsize=14)
    plt.xlabel('Time Period', fontsize=12)
    plt.ylabel('Growth Rate (%)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.xticks(YEARS[1:], YEAR_LABELS[1:])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'salary_growth_rate.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("Loading data...")
    male_data, female_data = load_data()
    
    print("\n1. Generating salary progression analysis...")
    analyze_salary_progression(male_data, female_data)
    
    print("2. Generating position distribution analysis...")
    analyze_position_distribution(male_data, female_data)
    
    print("3. Generating promotion trajectory analysis...")
    analyze_promotion_trajectory(male_data, female_data)
    
    print("4. Generating salary growth rate analysis...")
    analyze_salary_growth_rate(male_data, female_data)
    
    print(f"\nAnalysis complete! All results have been saved to the {output_dir} directory")

if __name__ == "__main__":
    main()