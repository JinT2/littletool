import re
import argparse

def extract_paths(input_file, output_file):
    try:
        # 打开输入文件读取内容
        with open(input_file, 'r', encoding='utf-8') as infile:
            data = infile.readlines()

        # 用于存储提取的路径
        paths = []

        # 更新正则表达式以匹配URL路径或独立路径
        url_pattern = re.compile(r'([^/]+)?(/[^\s,\"]+)')

        for line in data:
            matches = url_pattern.findall(line)
            for match in matches:
                # 提取路径部分并清理不必要的字符
                path = match[1].strip() if match[1] else match[0].strip()
                if path:  # 确保提取的路径不为空
                    paths.append(path)

        # 写入到输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("\n".join(paths))

        print(f"成功提取 {len(paths)} 个路径并保存到 {output_file}")

    except FileNotFoundError:
        print(f"文件 {input_file} 未找到，请检查文件名和路径！")
    except Exception as e:
        print(f"发生错误：{e}")

# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从文本文件中提取路径并保存到另一个文件中")
    parser.add_argument('-r', '--read', required=True, help="输入文件名")
    parser.add_argument('-w', '--write', required=True, help="输出文件名")
    args = parser.parse_args()

    extract_paths(args.read, args.write)
