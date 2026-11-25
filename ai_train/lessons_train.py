# -*- coding: utf-8 -*-
# AI 训练工程师路线（第一阶段：用 NumPy 从零训练）
# 每一课都是独立的：第一步会先写好这一课需要的开头几行。
LESSONS = [
    {
        "id": "T01",
        "title": "模型就是一个会调数字的公式",
        "steps": [
            {
                "say": "模型最简单的样子：输入 x，乘上 w，再加上 b，得到预测 y。\nw 和 b 就是要让电脑自己学会的数字。",
                "write": "w = 2.0\nb = 1.0\nx = 3.0\ny = w * x + b\nprint(y)",
                "mode": "last", "expect": "7.0",
                "hint": "y = w * x + b，* 是乘号。",
            },
            {
                "say": "NumPy 可以一次算很多个数。np.array 就是把一串数字装进数组。",
                "write": "import numpy as np\nxs = np.array([1.0, 2.0, 3.0])\nys = w * xs + b\nprint(ys)",
                "mode": "last", "expect": "[3. 5. 7.]",
                "hint": "xs 是数组，w * xs + b 会对每个数都做一遍。",
            },
        ],
    },
    {
        "id": "T02",
        "title": "误差：预测错了多少",
        "steps": [
            {
                "say": "这一课先照着写开头几行：数据 xs，真实答案 y_true，还有 w=1、b=1 的预测。\n然后算误差：误差 = 预测 - 真实。误差平方后求平均，叫 MSE（均方误差），数越小越准。",
                "write": "import numpy as np\nxs = np.array([1.0, 2.0, 3.0])\ny_true = np.array([3.0, 5.0, 7.0])\nw = 1.0\nb = 1.0\nys = w * xs + b\nerr = ys - y_true\nloss = np.mean(err ** 2)\nprint(loss)",
                "mode": "test",
                "check": "assert abs(loss - 14 / 3) < 1e-9, f'loss 应该约等于 4.667，现在是 {loss}'",
                "hint": "err ** 2 是每个误差平方，np.mean 是求平均。",
            },
        ],
    },
    {
        "id": "T03",
        "title": "梯度：往哪边调、调多少",
        "steps": [
            {
                "say": "梯度告诉我们：w 稍微变大一点，误差会变大还是变小。\n我们要往“误差变小”的方向调。下面用一个很小的数 eps 去试。",
                "write": "import numpy as np\nxs = np.array([1.0, 2.0, 3.0])\ny_true = np.array([3.0, 5.0, 7.0])\nw = 1.0\nb = 1.0\neps = 0.0001\ndef loss_of(w_try):\n    preds = w_try * xs + b\n    return np.mean((preds - y_true) ** 2)\ngrad_w = (loss_of(w + eps) - loss_of(w)) / eps\nprint(round(grad_w, 2))",
                "mode": "last", "expect": "-9.33",
                "hint": "def 下面的代码要缩进 4 个空格。",
            },
            {
                "say": "梯度是负数，说明 w 应该变大。\n更新规则：新的 w = 旧的 w - 学习率 × 梯度。学习率 lr 控制每次走多远。",
                "write": "lr = 0.05\nw = w - lr * grad_w\nprint(round(w, 3))",
                "mode": "last", "expect": "1.467",
                "hint": "w = w - lr * grad_w",
            },
        ],
    },
    {
        "id": "T04",
        "title": "梯度下降：重复很多次",
        "steps": [
            {
                "say": "这一课先照着写开头几行，然后把“算梯度、改 w”放进循环，重复 200 次。\n这就是训练，名字叫梯度下降。",
                "write": "import numpy as np\nxs = np.array([1.0, 2.0, 3.0])\ny_true = np.array([3.0, 5.0, 7.0])\nb = 1.0\nw = 1.0\nlr = 0.05\nfor step in range(200):\n    grad_w = np.mean(2 * (w * xs + b - y_true) * xs)\n    w = w - lr * grad_w\nprint(round(w, 2))",
                "mode": "test",
                "check": "assert abs(w - 2) < 0.01, f'训练后 w 应该接近 2，现在是 {w}'",
                "hint": "for 下面的代码要缩进 4 个空格。",
            },
        ],
    },
    {
        "id": "T05",
        "title": "同时学 w 和 b",
        "steps": [
            {
                "say": "这一课 w 和 b 都要学。它们各自有自己的梯度，每次都一起更新。\n先照着写开头几行，w 和 b 都从 0 开始。",
                "write": "import numpy as np\nxs = np.array([1.0, 2.0, 3.0])\ny_true = np.array([3.0, 5.0, 7.0])\nlr = 0.05\nw = 0.0\nb = 0.0\nfor step in range(2000):\n    err = w * xs + b - y_true\n    grad_w = np.mean(2 * err * xs)\n    grad_b = np.mean(2 * err)\n    w = w - lr * grad_w\n    b = b - lr * grad_b\nprint(round(w, 2), round(b, 2))",
                "mode": "test",
                "check": "assert abs(w - 2) < 0.01 and abs(b - 1) < 0.01, f'应该接近 w=2、b=1，现在是 w={w}, b={b}'",
                "hint": "两行梯度和两行更新都要写，for 里面都要缩进。",
            },
        ],
    },
    {
        "id": "T06",
        "title": "两层网络：一层接一层算",
        "steps": [
            {
                "say": "激活函数 relu 很简单：小于 0 的数变成 0，大于 0 的数保持不变。\n神经网络每一层都会用它，让模型能学到弯曲的规律。",
                "write": "import numpy as np\ndef relu(z):\n    return np.maximum(0, z)\nprint(relu(np.array([-2.0, 0.5, 3.0])))",
                "mode": "last", "expect": "[0.  0.5 3. ]",
                "hint": "np.maximum(0, z) 就是和 0 比较，取较大的那个。",
            },
            {
                "say": "两层的计算：先 h = relu(X × W1 + b1)，再 out = h × W2 + b2。\n@ 是矩阵乘法。X 的列数要等于 W1 的行数，形状才对得上。",
                "write": "import numpy as np\ndef relu(z):\n    return np.maximum(0, z)\nX = np.array([[1.0, 2.0]])\nW1 = np.array([[0.5, -1.0], [1.0, 0.5]])\nb1 = np.array([0.0, 0.0])\nW2 = np.array([[1.0], [2.0]])\nb2 = np.array([0.0])\nh = relu(X @ W1 + b1)\nout = h @ W2 + b2",
                "mode": "test",
                "check": "assert out.shape == (1, 1), f'形状应该是 (1, 1)，现在是 {out.shape}'\nassert abs(out[0, 0] - 2.5) < 1e-9, f'结果应该是 2.5，现在是 {out[0, 0]}'",
                "hint": "h = relu(X @ W1 + b1)，out = h @ W2 + b2",
            },
        ],
    },
    {
        "id": "T07",
        "title": "分类：让模型学会“是”或“不是”",
        "steps": [
            {
                "say": "分类题的输出要在 0 到 1 之间：接近 1 表示“是”，接近 0 表示“不是”。\nsigmoid 函数就是把任意数字压到 0 到 1 之间。",
                "write": "import numpy as np\ndef sigmoid(z):\n    return 1 / (1 + np.exp(-z))\nprint(round(float(sigmoid(0.0)), 2), round(float(sigmoid(4.0)), 2))",
                "mode": "last", "expect": "0.5 0.98",
                "hint": "return 1 / (1 + np.exp(-z))",
            },
            {
                "say": "用一个神经元学 OR 规则：两个输入里只要有一个是 1，结果就是 1。\n下面的代码会训练 2000 次，最后检查它是不是全学对了。",
                "write": "import numpy as np\ndef sigmoid(z):\n    return 1 / (1 + np.exp(-z))\nX = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)\nt = np.array([0, 1, 1, 1], dtype=float)\nw = np.zeros(2)\nb = 0.0\nlr = 0.5\nfor i in range(2000):\n    p = sigmoid(X @ w + b)\n    err = p - t\n    w = w - lr * (X.T @ err) / len(t)\n    b = b - lr * np.mean(err)\npred = sigmoid(X @ w + b)",
                "mode": "test",
                "check": "assert ((pred > 0.5) == (t == 1)).all(), f'预测结果是 {pred}，应该和 [0,1,1,1] 一致'",
                "hint": "for 里面的 4 行都要缩进 4 个空格。",
            },
        ],
    },
    {
        "id": "T08",
        "title": "训练集和测试集：别只看考过的题",
        "steps": [
            {
                "say": "数据要分成两份：训练集用来学，测试集用来考。\n只看训练集的成绩，可能只是背下了答案。",
                "write": "import numpy as np\ndata_x = np.arange(10).reshape(10, 1).astype(float)\ndata_y = (data_x[:, 0] > 4).astype(float)\ntrain_x, test_x = data_x[:8], data_x[8:]\ntrain_y, test_y = data_y[:8], data_y[8:]\nprint(len(train_x), len(test_x))",
                "mode": "last", "expect": "8 2",
                "hint": "前 8 个是训练集，后 2 个是测试集。",
            },
            {
                "say": "准确率 = 答对的数量 ÷ 总数量。\nnp.mean 对 True/False 会当成 1 和 0 来求平均，所以能直接算准确率。",
                "write": "import numpy as np\ndef accuracy(pred, true):\n    return np.mean(pred == true)\nprint(accuracy(np.array([1, 0, 1]), np.array([1, 1, 1])))",
                "mode": "last", "expect": "0.6666666666666666",
                "hint": "pred == true 得到每题对不对，np.mean 求平均就是准确率。",
            },
        ],
    },
]
