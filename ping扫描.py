import subprocess
import platform
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def ping_ip(ip_address):
    """
    使用ping命令检测IP地址是否存活
    :param ip_address: 要检测的IP地址
    :return: True if the IP is reachable, False otherwise
    """
    # 根据操作系统选择ping命令的参数
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    # 执行ping命令
    response = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 如果返回值为0，表示IP地址存活
    return response == 0

def parse_ip_input(ip_input):
    """
    解析输入的IP地址，支持以下格式：
    - 单个IP：1.1.1.1
    - 多个IP（逗号或分号分隔）：1.1.1.1,1.1.1.2;1.1.1.3
    - IP范围：1.1.1.1-30
    :param ip_input: 输入的IP地址字符串
    :return: 返回解析后的IP地址列表
    """
    ip_list = []

    # 处理逗号或分号分隔的多个IP
    if ',' in ip_input or ';' in ip_input:
        # 替换分号为逗号，统一处理
        ip_input = ip_input.replace(';', ',')
        # 按逗号分割
        ip_list.extend(ip_input.split(','))
    # 处理IP范围（如1.1.1.1-30）
    elif '-' in ip_input:
        base_ip, end = ip_input.split('-')
        # 提取IP的前三部分（如1.1.1）
        base_parts = base_ip.split('.')
        if len(base_parts) != 4:
            raise ValueError(f"Invalid IP range format: {ip_input}")
        # 生成范围内的所有IP
        start = int(base_parts[3])
        for i in range(start, int(end) + 1):
            ip_list.append(f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}")
    # 处理单个IP
    else:
        ip_list.append(ip_input)

    # 去除可能的空白字符
    ip_list = [ip.strip() for ip in ip_list if ip.strip()]
    return ip_list

def read_ips_from_file(file_path):
    """
    从文件中读取IP地址
    :param file_path: 文件路径
    :return: 返回所有解析后的IP地址列表
    """
    all_ips = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # 忽略空行
                all_ips.extend(parse_ip_input(line))
    return all_ips

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Ping IP addresses from a file.", add_help=False)
    parser.add_argument('-r', '--file', required=True, help="Path to the file containing IP addresses.")
    parser.add_argument('-t', '--threads', type=int, default=10, help="Number of threads to use (default: 10).")
    parser.add_argument('-o', '--output', help="Path to the output file to save reachable IPs.")
    parser.add_argument('-h', '--help', action='help', help="Show this help message and exit.")
    args = parser.parse_args()

    # 从文件中读取IP地址
    try:
        ip_list = read_ips_from_file(args.file)
        print(f"Loaded IPs: {len(ip_list)} IPs to check.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 使用多线程检测IP地址
    reachable_ips = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_ip = {executor.submit(ping_ip, ip): ip for ip in ip_list}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    reachable_ips.append(ip)
                    print(f'{ip} is reachable.')
            except Exception as e:
                print(f'{ip} generated an exception: {e}')

    # 输出存活的IP地址到文件
    if args.output:
        with open(args.output, 'w') as output_file:
            for ip in reachable_ips:
                output_file.write(ip + '\n')
        print(f"Reachable IPs saved to {args.output}.")

if __name__ == '__main__':
    main()