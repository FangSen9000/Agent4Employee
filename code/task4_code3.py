import csv
import re

def extract_and_save_data(input_file, output_file, symbol, max_lines=100):
    """
    从 CSV 文件中提取包含指定符号的完整数字，所有提取的数字摊平后，每 5 个数字存储为一行。
    """
    all_numbers = []  # 存储所有提取到的数字
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            for cell in row:
                # 查找包含符号的部分，并提取符号后面的完整数字
                if symbol in cell:
                    match = re.search(fr'{re.escape(symbol)}(\d+)', cell)
                    if match:
                        number = int(match.group(1))  # 提取完整数字并转为整数
                        all_numbers.append(number)  # 添加到数字列表
                        print(f"Extracted number: {number}")  # 调试输出

    # 将所有数字按照每 5 个分为一组存储，最多存储 max_lines 行
    results = [all_numbers[i:i+5] for i in range(0, len(all_numbers), 5)][:max_lines]

    # 将结果存储到输出文件
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(results)

# 处理两个输入文件
extract_and_save_data(
    '/research/cbim/vast/mz751/Projects/Fairness/女_predictions_year_salary.csv',
    '/research/cbim/vast/mz751/Projects/Fairness/female_salary.csv',
    '$'
)
extract_and_save_data(
    '/research/cbim/vast/mz751/Projects/Fairness/男_predictions_year_salary.csv',
    '/research/cbim/vast/mz751/Projects/Fairness/male_salary.csv',
    '$'
)
