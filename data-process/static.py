if __name__ == '__main__':
    with open('train.source') as f:
        max_s_count = 0  # 初始化最大值
        for line in f:
            s_count = line.count('<S>')  # 计算当前行中 <S> 的个数
            p_count = line.count('<P>')
            o_count = line.count('<O>')
            sum_count = s_count + p_count + o_count
            if sum_count > max_s_count:
                max_s_count = sum_count  # 更新最大值
        print(f"最大 <S> 个数: {max_s_count}")  # 输出最大值
        