import numpy as np

class Topsis():
    evaluation_matrix = np.array([])  # 评价矩阵
    weighted_normalized = np.array([])  # 加权归一化矩阵
    normalized_decision = np.array([])  # 归一化决策矩阵
    M = 0  # 行数（备选方案数）
    N = 0  # 列数（标准数）

    '''
    创建一个包含 m 个备选方案和 n 个标准的评价矩阵，
    每个备选方案和标准的交集给定为 x_ij，因此我们有一个矩阵 (x_ij)_{m×n}。
    '''

    def __init__(self, evaluation_matrix, weight_matrix, criteria):
        # M×N 矩阵
        self.evaluation_matrix = np.array(evaluation_matrix, dtype="float")

        # M 个备选方案（选项）
        self.row_size = len(self.evaluation_matrix)

        # N 个标准
        self.column_size = len(self.evaluation_matrix[0])

        # N 大小的权重矩阵
        self.weight_matrix = np.array(weight_matrix, dtype="float")
        self.weight_matrix = self.weight_matrix / sum(self.weight_matrix)
        self.criteria = np.array(criteria, dtype="float")

    '''
    # 第 2 步
    将矩阵 (x_ij)_{m×n} 归一化，形成矩阵
    '''

    def step_2(self):
        # 归一化评分
        self.normalized_decision = np.copy(self.evaluation_matrix)
        sqrd_sum = np.zeros(self.column_size)
        for i in range(self.row_size):
            for j in range(self.column_size):
                sqrd_sum[j] += self.evaluation_matrix[i, j]**2
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.normalized_decision[i, j] = self.evaluation_matrix[i, j] / (sqrd_sum[j]**0.5)

    '''
    # 第 3 步
    计算加权归一化决策矩阵
    '''

    def step_3(self):
        self.weighted_normalized = np.copy(self.normalized_decision)
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.weighted_normalized[i, j] *= self.weight_matrix[j]

    '''
    # 第 4 步
    确定最差备选方案 A_w 和最优备选方案 A_b：
    '''

    def step_4(self):
        self.worst_alternatives = np.zeros(self.column_size)
        self.best_alternatives = np.zeros(self.column_size)
        for i in range(self.column_size):
            if self.criteria[i]:
                self.worst_alternatives[i] = min(self.weighted_normalized[:, i])
                self.best_alternatives[i] = max(self.weighted_normalized[:, i])
            else:
                self.worst_alternatives[i] = max(self.weighted_normalized[:, i])
                self.best_alternatives[i] = min(self.weighted_normalized[:, i])

    '''
    # 第 5 步
    计算目标备选方案 i 与最差解 A_w 之间的 L2 距离
    d_{iw} = \sqrt{\sum_{j=1}^{n}(t_{ij}-t_{wj})^2}, i=1,2,...,m
    以及备选方案 i 与最优解 A_b 之间的距离
    d_{ib} = \sqrt{\sum_{j=1}^{n}(t_{ij}-t_{bj})^2}, i=1,2,...,m
    其中 d_{iw} 和 d_{ib} 分别是目标备选方案 i 到最差和最优解的 L2 距离。
    '''

    def step_5(self):
        self.worst_distance = np.zeros(self.row_size)
        self.best_distance = np.zeros(self.row_size)

        self.worst_distance_mat = np.copy(self.weighted_normalized)
        self.best_distance_mat = np.copy(self.weighted_normalized)

        for i in range(self.row_size):
            for j in range(self.column_size):
                self.worst_distance_mat[i][j] = (self.weighted_normalized[i][j] - self.worst_alternatives[j]) ** 2
                self.best_distance_mat[i][j] = (self.weighted_normalized[i][j] - self.best_alternatives[j]) ** 2

                self.worst_distance[i] += self.worst_distance_mat[i][j]
                self.best_distance[i] += self.best_distance_mat[i][j]

        for i in range(self.row_size):
            self.worst_distance[i] = self.worst_distance[i] ** 0.5
            self.best_distance[i] = self.best_distance[i] ** 0.5

    '''
    # 第 6 步
    计算与最差解的相似度
    '''

    def step_6(self):
        np.seterr(all='ignore')
        self.worst_similarity = np.zeros(self.row_size)
        self.best_similarity = np.zeros(self.row_size)

        for i in range(self.row_size):
            # 计算与最差解的相似度
            self.worst_similarity[i] = self.worst_distance[i] / (self.worst_distance[i] + self.best_distance[i])

            # 计算与最优解的相似度
            self.best_similarity[i] = self.best_distance[i] / (self.worst_distance[i] + self.best_distance[i])

    def ranking(self, data):
        # 使用方案名称（A、B、C）进行排名
        alternatives = ['A', 'B', 'C']
        sorted_indices = data.argsort()
        return [alternatives[i] for i in sorted_indices]

    def rank_to_worst_similarity(self):
        # 返回与最差解的相似度排名
        return self.ranking(self.worst_similarity)

    def rank_to_best_similarity(self):
        # 返回与最优解的相似度排名
        return self.ranking(self.best_similarity)

    def calc(self):
        print("第 1 步\n", self.evaluation_matrix, end="\n\n")
        self.step_2()
        print("第 2 步\n", self.normalized_decision, end="\n\n")
        self.step_3()
        print("第 3 步\n", self.weighted_normalized, end="\n\n")
        self.step_4()
        print("第 4 步\n", self.worst_alternatives,
              self.best_alternatives, end="\n\n")
        self.step_5()
        print("第 5 步\n", self.worst_distance, self.best_distance, end="\n\n")
        self.step_6()
        print("第 6 步\n", self.worst_similarity,
              self.best_similarity, end="\n\n")


# 评价矩阵（每个方案在不同标准下的得分）
evaluation_matrix = [
    [500, 80, 70, 70],  # 方案 A
    [450, 85, 75, 75],  # 方案 B
    [600, 90, 65, 80],  # 方案 C
]

# 标准权重
weight_matrix = [0.2, 0.3, 0.25, 0.25]

# 标准类型（0为成本型，1为效益型）
criteria = [0, 1, 1, 1]

# 创建 Topsis 类实例
topsis = Topsis(evaluation_matrix, weight_matrix, criteria)

# 执行 TOPSIS 计算并输出结果
topsis.calc()

# 输出与最优解的相似度排名
print("与最优解的相似度排名：", topsis.rank_to_best_similarity())
