import sys
import math
import operator

def completlink(wordnum, sim):
    mergelist = []
    assign = {}
    eliminated = {}
    for n in range(wordnum):
        assign[n] = n
        eliminated[n] = 0
    for k in range(wordnum - 1):
        max = -1
        cl1 = -1
        cl2 = -1
        for n in range(wordnum):
            if eliminated[n]:
                continue
            for i in range(n):
                if eliminated[i]:
                    continue
                if sim[n][i] > max:
                    max = sim[n][i]
                    cl1 = i
                    cl2 = n
        assert cl1 >= 0 and cl2 >= 0
        eliminated[cl1] = 1
        mergelist.append([cl1, cl2])
        for n in range(wordnum):
            if assign[n] == cl1:
                assign[n] = cl2
        for n in range(wordnum):
            if eliminated[n]:
                continue
            if sim[cl1][n] < sim[cl2][n]:
                smallersim = sim[cl1][n]
                sim[cl2][n] = smallersim
                sim[n][cl2] = smallersim
    return mergelist, sim, assign, eliminated

def clustering(wordnum, mergelist, aftermat, th):
    clustered = {}
    for n in range(wordnum):
        clustered[n] = n
    for m in mergelist:
        if aftermat[m[0]][m[1]] >= th:
            for n in range(wordnum):
                if clustered[n] == m[0]:
                    clustered[n] = m[1]
    check = {}
    for n in range(wordnum):
        check[n] = -1
    cnt = 0
    for n in range(wordnum):
        if check[clustered[n]] == -1:
            cnt+=1
            check[clustered[n]] = cnt
            clustered[n] = cnt
        else:
            clustered[n] = check[clustered[n]]
    clusters = {}
    for n in range(1, cnt+1):
        clusters[n] = []
    for n in range(wordnum):
        clusters[clustered[n]].append(n)
    return clustered, cnt, clusters


def computesimmat(wordnum, word_vecs, mode):
    assert mode == 'cos' or mode == 'euc'
    sourcedata = {}
    for n in range(wordnum):
        sourcedata[n] = {}
    # for n in range(wordnum):
    #     sourcedata[n][n] = 0
    for n in range(wordnum):
        for i in range(n, wordnum):
            if mode == 'cos':
                sim = -computesimcos(word_vecs[n], word_vecs[i])
            else:
                sim = -computesimeuc(word_vecs[n], word_vecs[i])
            sourcedata[n][i] = sim
            sourcedata[i][n] = sim
    return sourcedata


def vec_sub(v1, v2):
    ret = []
    for i in range(len(v1)):
        ret.append(v1[i] - v2[i])
    return ret


def dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))


def eucllen(v):
    return math.sqrt(dot_product(v, v))


def vector_cos(v1, v2):
    prod = dot_product(v1, v2)
    len1 = eucllen(v1)
    len2 = eucllen(v2)
    return prod / (len1 * len2)


def computesimcos(v1, v2):
    cossim = vector_cos(v1, v2)
    return cossim


def computesimeuc(v1, v2):
    dist = eucllen(vec_sub(v1, v2))
    return dist


# def normalizevec(v):
#     ret = []
#     for num in v:
#         newnum = (num+1)/2
#         newnum = newnum / math.sqrt(300)
#         ret.append(newnum)
#     return ret

# def normalizeword_vecs(word_vecs):
#     normed_vecs = []
#     for vec in word_vecs:
#         normed_vecs.append(normalizevec(vec))
#     return normed_vecs

def normalizesim(wordnum, oldmatrix):
    newmatrix = {}
    maxnum = -1000
    minnum = 1000
    maxn = -1000
    for n in range(wordnum):
        for i in range(wordnum):
            if oldmatrix[n][i] > maxnum:
                maxnum = oldmatrix[n][i]
            if oldmatrix[n][i] < minnum:
                minnum = oldmatrix[n][i]
    for n in range(wordnum):
        newmatrix[n] = {}
        for i in range(wordnum):
            if (n == i):
                newmatrix[n][n] = 1.0
            else:
                newmatrix[n][i] = (oldmatrix[n][i] - minnum) / (maxnum - minnum)
                if newmatrix[n][i] > maxn:
                    maxn = newmatrix[n][i]
    assert maxn <= 1
    return newmatrix


input_file = open("WordEmbedding.txt", 'r')

lines = input_file.readlines()
words = []
word_vecs = []

cnt = 0
for line in lines:
    cnt += 1
    if (cnt % 2 == 1):
        words.append(line)
    else:
        word_vecs.append([float(i) for i in line.split(',')])

output_file = open("WordClustering.txt", 'w')



# matcheck_file = open("matcheck.txt", 'w')
wordnum = 338
# mode = 'euc'
# th = 0.15
mode = sys.argv[1]
th = float(sys.argv[2])
print("similarity :", mode)
print("thershold :",th)
if (mode == 'cos'):
    simmatrix = computesimmat(wordnum, word_vecs, mode)
    normedmat = normalizesim(wordnum, simmatrix)
    # for i in range(wordnum):
    #     for j in range(wordnum):
    #         assert 1 >= normedmat[i][j] >= 0
    #         matcheck_file.write(str(normedmat[i][j]) + ' ')
    #     matcheck_file.write("\n")
    mergelist, aftermat, assigned, eliminated = completlink(wordnum, normedmat)
    clustered, cnum, clusters = clustering(wordnum, mergelist, aftermat, th)
    print("cluster number:", cnum)
    # print(len(mergelist))
    # for m in mergelist:
    #     print(aftermat[m[0]][m[1]])
elif (mode == 'euc'):
    #     normed_vecs = normalizeword_vecs(word_vecs)
    simmatrix = computesimmat(wordnum, word_vecs, mode)
    normedmat = normalizesim(wordnum, simmatrix)
    # for i in range(wordnum):
    #     for j in range(wordnum):
    #         assert 1 >= normedmat[i][j] >= 0
    #         matcheck_file.write(str(normedmat[i][j]) + ' ')
    #     matcheck_file.write("\n")
    mergelist, aftermat, assigned, eliminated = completlink(wordnum, normedmat)
    clustered, cnum, clusters = clustering(wordnum, mergelist, aftermat, th)
    print("cluster number:",cnum)
    # print(len(mergelist))
    # for m in mergelist:
    #     print(aftermat[m[0]][m[1]])

for i in range(wordnum):
    output_file.write(words[i])
    for nums in word_vecs[i]:
        output_file.write(str(nums) + ',')
    output_file.write("\n")
    output_file.write(str(clustered[i]) + '\n')


# wordtopci read
topic_file = open("WordTopic.txt", 'r')
tlines = topic_file.readlines()
cnt = 0
tcnt = 0
tncnt = 0
topicofword = {}
wordsoftopic = {}
for line in tlines:
    if line[0] == '[':
        nowtopic = tcnt
        tcnt += 1
        tncnt = 0
    elif len(line) <= 1:
        continue
    else:
        topicofword[cnt] = nowtopic
        cnt += 1
        tncnt +=1
        wordsoftopic[nowtopic] = tncnt

# print("tcnt:", tcnt)
#
# for e in wordsoftopic:
#     print(wordsoftopic[e])
# for e in topicofword:
#     print(topicofword[e])

input_file.close()
output_file.close()
topic_file.close()

# information gain
infogain = 0
# total entropy
totalent = 0
for n in range(tcnt):
    totalent += -(wordsoftopic[n]/wordnum * math.log(wordsoftopic[n]/wordnum,2))
# sub entropy sum
# print("totalent :",totalent)
subsum = 0
# print("!!")
# for n in clusters:
#     print(n,":", clusters[n])
for n in range(1, cnum+1):
    clen = len(clusters[n])
    subent = 0
    subcnt = {}
    for i in range(tcnt):
        subcnt[i] = 0
    for i in range(clen):
        subcnt[topicofword[clusters[n][i]]]+=1
    for i in range(tcnt):
        if subcnt[i] == 0 :
            continue
        subent += -(subcnt[i]/clen * math.log(subcnt[i]/clen, 2))
    subsum += (clen/wordnum) * subent
infogain = totalent - subsum
# print("subsum :",subsum)
print("infogain:",infogain)
# matcheck_file.close()

