import csv

def compare_csv_files(file_a, file_b):
    """
    比较两个文件中每一行最后一个数字，统计 A > B, B > A 和 A == B 的数量。
    """
    a_bigger = 0
    b_bigger = 0
    equal = 0

    with open(file_a, 'r', encoding='utf-8') as fa, open(file_b, 'r', encoding='utf-8') as fb:
        reader_a = csv.reader(fa)
        reader_b = csv.reader(fb)

        for row_a, row_b in zip(reader_a, reader_b):
            try:
                # 获取每行最后一个数字
                last_a = int(row_a[-1])
                last_b = int(row_b[-1])

                if last_a > last_b:
                    a_bigger += 1
                elif last_b > last_a:
                    b_bigger += 1
                else:
                    equal += 1
            except (ValueError, IndexError):
                # 跳过格式错误的行
                continue

    print(f"A > B: {a_bigger}")
    print(f"B > A: {b_bigger}")
    print(f"A == B: {equal}")

# 比较处理后的文件
compare_csv_files('/research/cbim/vast/mz751/Projects/Fairness/male_salary.csv', '/research/cbim/vast/mz751/Projects/Fairness/female_salary.csv')
