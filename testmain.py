import psutil
import os
import datetime
from FLUMModel.PreProcess import GetISet
from FLUMModel.Handlers import FLUMHandler
from FLUMModel.AssignParticipants import AssignParticipants,PrintInf
from FLUMModel.GetTruthNum import GetTruthNum
def comp(P, Q):
    if(len(P) != len(Q)):
        return 0
    for i in range(len(P)):
        if P[i] != Q[i]:
           return 0
    return 1

def GetAns(DataSet, Clientnum, Partinum, epsilon1, epsilon2, epsilon3, add, Minutil):
    begin0 = datetime.datetime.now()
    # 这里执行：选择参与者；生成参与者档案的操作
    # ！！！！注意：还没执行生成敏感度的操作！！！！
    participants, I = AssignParticipants(DataSet, Clientnum, Partinum, epsilon1, epsilon2, epsilon3, add)

    # maxlen是参与者数据集的事务最大长度，被用来限制需要生成的候选模式长度
    maxlen = 0
    for i in participants:
        if maxlen < i.T_lmax:
            maxlen = i.T_lmax
    # print("I: ",I)

    # 不是所有客户都生成档案，只有参与者生成档案
    # 注意：这个运行时间是不包括客户机分配和本地生成位图的时间
    handler = FLUMHandler(I, participants, Minutil, maxlen, 1)
    accept = handler.run()

    end_all = datetime.datetime.now()

    # print("-----------------------------------------")
    prepratitime = ((end_all - begin0).seconds - handler.server.servertime / (1000 * 1000)) / Partinum
    # print("一个参与者的平均运行时间： ", str(prepratitime))
    # print(participants[0].Time)
    # print("服务器运行时间 (s):" + str(handler.server.servertime / (1000 * 1000)))

    AllTime = (end_all - begin0).seconds + (end_all - begin0).microseconds / 1000 / 1000
    # print("FLUPM Total running time:", str(end_all - begin0), AllTime)
    # print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))
    # print("-----------------------------------------")

    # print("高效用模式为： ")
    # print(" High-utility itemsets count : ", len(accept))

    # for i in accept:
    #     print(i.pattern, i.utility)

    handler = FLUMHandler(I, participants, Minutil, maxlen, 0)
    Truth = handler.run()
    # print("len(accept): ", len(accept), "  Truth : ", len(Truth))
    tp = 0
    if (len(accept) > len(Truth)):
        for i in accept:
            for j in Truth:
                if (comp(i.pattern, j.pattern) == 1):
                    tp = tp + 1
    else:
        for i in Truth:
            for j in accept:
                if (comp(i.pattern, j.pattern) == 1):
                    tp = tp + 1
    # print("tp: ",tp)
    precision = 0
    recall = 0
    F1score = 0
    if len(accept) != 0:
        precision = tp / len(accept)
    if len(Truth) != 0:
        recall = tp / len(Truth)
    if (precision != 0 or recall != 0):
        F1score = 2 * precision * recall / (precision + recall)

    # print("Precision: %.2f; Recall: %.2f" % (precision,recall))
    # print("F1score: ", F1score)

    RE = (len(accept) - len(Truth)) / len(Truth) * 100
    return AllTime, F1score
    # print("RE: ",RE)

if __name__ == '__main__':
    DB_name = "liquor_5.txt"
    DataSet = "Dataset/Input/" + DB_name
    # Clientnum表示客户机的数目，用于划分数据集DataSet为Clientnum个客户数据集，PreClientTnum表示一个客户数据集的事务数目
    Clientnum = 100
    # ClientTransNum = [20,20,20,20,20]
    Partinum = 10
    # 注意： 自己检查代码结果正确时，进行实验比较的时候，需要找到参与者用的数据集（基准算法用）
    # 注意：在真正实验比较的时候，基准算法也应该用的是这些参与者用的数据集，而不是完整大数据集，不然结果肯定有问题，因为选取子数据集，模式的效用大概率比总数据集小
    # Minutil =  15000
    # sensitivety = 0.5
    epsilon1 = 20
    epsilon2 = 40
    epsilon3 = 40
    # 注意：由于参与者的数量变多，在划分数据集时会导致有些事务被舍弃（数目为add)，为了避免这种情况，把被舍弃的数据添加到最后一个参与者数据集中。
    add = 0

    listu = [11000, 12000, 13000, 14000, 15000]
    T = []
    for Minutil in listu:
        print("minutil: ", Minutil)
        sumTime = 0
        sumF1score = 0
        for i in range(10):
            AllTime, F1score = GetAns(DataSet, Clientnum, Partinum, epsilon1, epsilon2, epsilon3, add, Minutil)
            sumTime = sumTime + AllTime
            sumF1score = sumF1score + F1score

        # print("")
        # T.append(sumTime / 50)
        print("AvgTime: (s)", sumTime / 10, "AvgF1score: ", sumF1score / 10)

