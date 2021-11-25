from konlpy.tag import Mecab
from pymongo import MongoClient
import copy

stop_word = dict()
DBname = "db20161598"
conn = MongoClient("localhost")
db = conn[DBname]
db.authenticate(DBname, DBname)

#stop word는 불용어 사전, 뉴스 분석하는데 필요가 없는 단어들을 모아놓은 사전
def make_stop_word():
    f = open("wordList.txt", "r")
    while True:
        line = f.readline()
        if not line:
            break
        stop_word[line.strip()] = True
    f.close()

def p0():
    col1 = db['news']
    col2 = db['news_freq']

    col2.drop() 

    for doc in col1.find():
        contentDic = dict()
        for key in doc.keys():
            if key != "_id":        #_id는 document의 primary key
                contentDic[key] = doc[key]
        col2.insert(contentDic)

def p1():
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update({"_id": doc['_id']}, doc)

def morphing(content):
    mecab = Mecab()
    morphList = []
    for word in mecab.nouns(content):
        if word not in stop_word:
            morphList.append(word)
    return morphList

#print morphs 함수, freq  collection 출력
def p2():
    col = db['news_freq']
    news = dict()
    news = col.find_one()
    mor = news['morph']
    for x in mor:
        print(x)

def p3():
    col1 = db['news_freq']
    col2 = db['news_wordset']
    col2.drop()
    for doc in col1.find():
        new_doc = dict()
        new_set = set()
        for w in doc['morph']:
            new_set.add(w)
        new_doc['word_set'] = list(new_set)
        new_doc['news_freq_id'] = doc['_id']
        col2.insert(new_doc)

#print wordset 함수, word set collection 출력 
def p4():
    col = db['news_wordset']
    news = dict()
    news = col.find_one()
    wordset = news['word_set']
    for x in wordset:
        print(x)

def p5(length):
    make_dataset()	
   
    #이름 생성
    can_name = "candidate_L"
    can_name += str(length)
    col = db[can_name]
    
    col.drop()

    initSet = initialize_set(data_set)
    FP_TR, HD_TB = make_FPTree(initSet, min_sup,freq_flag=False)
    freqItems_sup = dict()
    freqItems = []
    mining(FP_TR, HD_TB, min_sup, set([]), freqItems, freqItems_sup)
    
    #print(freqItems_sup)
    #길이 같은 경우만 출력
    
    global freq_i
    freq_i = freqItems

    cnt = 0
    for x in freqItems:
        if(len(x)==length):
            list_of_set = list(x)
            if length == 1:
                col.insert({"item_set":list(x), "support":HD_TB[list_of_set[0]][0]})
            elif length == 2:
                col.insert({"item_set":list_of_set, "support":freq_item_sup(list_of_set)})
            else:
                col.insert({"item_set":list_of_set, "support":freq_item_sup(list_of_set)})
                    
            
			
def p6(length):
    col1 = db["candidate_L1"]
    col2 = db["candidate_L2"]
    col3 = db["candidate_L3"]
    
    min_con = 0.8

    if length == 2:
        word2_set = col2.find()
        for word2 in word2_set:
            st_set = word2["item_set"]
            st_sup = word2["support"]
            l_sup = 0
            r_sup = 0
            word1_set = col1.find()
            for word1 in word1_set:
                word1_set = word1["item_set"]
                if st_set[0] == word1_set[0]:
                    l_sup = word1["support"]
                if st_set[1] == word1_set[0]:
                    r_sup = word1["support"]
            
            #calculate confidence
            con = (float(st_sup) / float(l_sup))
            if con >= min_con:
                print(st_set[0],"=>",st_set[1],"\t", con)
            con = (float(st_sup) / float(r_sup))
            if con >= min_con:
                print(st_set[1],"=>",st_set[0],"\t",con)

    elif length == 3:
        word3_set = col3.find()
        for word3 in word3_set:
            st_set = word3["item_set"]
            st_sup = word3["support"]

            word1_set = col1.find()
            for word1 in word1_set:
                word1_set = word1["item_set"]
                if st_set[0] == word1_set[0]:
                    zero_sup = word1["support"]
                if st_set[1] == word1_set[0]:
                    one_sup = word1["support"]
                if st_set[2] == word1_set[0]:
                    two_sup = word1["support"]
            
            z_o = [st_set[0], st_set[1]]
            z_t = [st_set[0], st_set[2]]
            o_t = [st_set[1], st_set[2]]

            z_o_sup = 0
            z_t_sup = 0
            o_t_sup = 0
            
            #print(z_o, z_t, o_t)

            word2_set = col2.find()
            for word2 in word2_set:
                word2_set = word2["item_set"]
                #print(word2_set)
                if z_o[0] in  word2_set and z_o[1] in word2_set:
                    z_o_sup = word2["support"]
                if z_t[0] in word2_set and z_t[1] in word2_set:
                    z_t_sup = word2["support"]
                if o_t[0] in word2_set and o_t[1] in word2_set:
                    o_t_sup = word2["support"]

            #calculate confidence
            con = (float(st_sup) / float(zero_sup))
            if con >= min_con:
                print(st_set[0],"=>",o_t[0],",",o_t[1],"\t", con)
            con = (float(st_sup) / float(one_sup))
            if con >= min_con:
                print(st_set[1],"=>",z_t[0],",",z_t[1],"\t", con)
            con = (float(st_sup) / float(two_sup))
            if con >= min_con:
                print(st_set[2],"=>",z_o[0],",",z_o[1],"\t", con)
           
            if z_o_sup != 0:
                con = (float(st_sup) / float(z_o_sup))
                if con >= min_con:
                    print(z_o[0],",",z_o[1],"=>",st_set[2],"\t", con) 
            if z_t_sup != 0:
                con = (float(st_sup) / float(z_t_sup))
                if con >= min_con:
                    print(z_t[0],",",z_t[1],"=>",st_set[1],"\t", con)
            if o_t_sup != 0:
                con = (float(st_sup) / float(o_t_sup))
                if con >= min_con:
                    print(o_t[0],",", o_t[1],"=>",st_set[0],"\t", con)





#making dataset
def make_dataset():
    col = db['news_wordset']
    word_col = col.find()
    #news의 총 개수 저장, min_sup 저장
    global news_num 
    news_num = word_col.count()
    global min_sup 
    min_sup = news_num * 0.04
    global data_set
    data_set = list()
	
    for wordset in word_col:
        temp = wordset['word_set']
        data_set.append(temp)

def initialize_set(dataSet):
    retDict={}
    for trans in dataSet:
	    key = frozenset(trans)
	    if key in retDict:
	        retDict[frozenset(trans)] += 1
	    else:
		    retDict[frozenset(trans)] = 1
    return retDict

class treeNode:
    def __init__(self, name, support, parent):
        self.name = name
        self.sup = support
        self.linked_li = None
        self.parent = parent
        self.child = {}
    
    def increase(self, support):
        self.sup += support

def update_header(nodeToTest, targetNode):
    while nodeToTest.linked_li != None:
        nodeToTest = nodeToTest.linked_li
    nodeToTest.linked_li = targetNode
	
def update_fptree(items, inTree, HT, count):
    if items[0] in inTree.child:
        inTree.child[items[0]].increase(count)
    else:
        inTree.child[items[0]] = treeNode(items[0], count, inTree)
        if HT[items[0]][1] == None:
            HT[items[0]][1] = inTree.child[items[0]]
        else:
            update_header(HT[items[0]][1], inTree.child[items[0]])
    if len(items) > 1:
        update_fptree(items[1::], inTree.child[items[0]], HT, count)

def freq_item_sup(lt):
    cnt = 0
    for word_set in data_set:
        l_flag = 0
        if lt[0] in word_set:
            l_flag += 1
        if lt[1] in word_set:
            l_flag += 1
        if len(lt) == 3:
            if lt[2] in word_set:
                l_flag += 1
            if l_flag == 3:
                cnt += 1
        if len(lt) == 2:
            if l_flag == 2:
                cnt += 1
    return cnt


def make_FPTree(dataSet, min_sup=1, freq_flag = True):
    HT = {}
    for trans in dataSet:
        for item in trans:
            HT[item] = HT.get(item,0)+dataSet[trans]
    temp_header = HT.copy()
    for k in temp_header.keys():
        if HT[k] < min_sup:
            del(HT[k])
    freqItemSet = set(HT.keys())
    if len(freqItemSet) == 0:
        return None, None
    for k in HT:
        HT[k] = [HT[k], None] 
    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:
            if item in freqItemSet: 
                localD[item] = HT[item][0]
        if len(localD) > 0:
            orderedItem = [v[0] for v in sorted(localD.items(), key=lambda p:(p[1], p[0]), reverse=True)]
            update_fptree(orderedItem, retTree, HT, count)
    return retTree, HT


def ascend_fptree(leafNode, prefix_path):
    if leafNode.parent != None:
        prefix_path.append(leafNode.name)
        ascend_fptree(leafNode.parent, prefix_path)

def find_prefix(pattern, HD_TB):
    treeNode = HD_TB[pattern][1]
    condPats = {}
    while treeNode != None:
        prefix_path = []
        ascend_fptree(treeNode, prefix_path) 
        if len(prefix_path) > 1:
            condPats[frozenset(prefix_path[1:])] = treeNode.sup 
        treeNode = treeNode.linked_li
    return condPats

def mining(inTree, HT, min_sup, preFix, freqItemList, freqItem_sup):
    bigL = [v[0] for v in sorted(HT.items(), key=lambda p:p[1][0])] 
    for pattern in bigL: 
        newFreqSet = preFix.copy()
        newFreqSet.add(pattern)
        #print("pattern : ",pattern)
        #print("HT : ",HT[pattern])
        freqItem_sup[frozenset(pattern)]=HT[pattern][0]
        freqItemList.append(newFreqSet)
        cond_pat = find_prefix(pattern, HT)
        cond_tree, head = make_FPTree(cond_pat, min_sup, freq_flag=True) 
        if head != None:
            mining(cond_tree, head, min_sup, newFreqSet, freqItemList, freqItem_sup) 


def printMenu():
    print("0. CopyData")
    print("1. Morph")
    print("2. print morphs")
    print("3. print wordset")
    print("4. frequent item set")
    print("5. association rule")

if __name__ == "__main__":
    make_stop_word()
    printMenu()
    selector = int(input())

    if selector == 0:
        p0()
    elif selector == 1:
        p1()
        p3()
    elif selector == 2:
        p2()
    elif selector == 3:
        p4()
    elif selector == 4:
        print("input length of the frequent item:")
        length = int(input())
        p5(length)
    elif selector == 5:
        print("input length of the frequent item:")
        length = int(input())
        p6(length)
