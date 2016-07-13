# -*- coding: utf-8 -*-
import scipy.sparse as sp
import numpy as np
import time
import inspect
import os


# parameter 
class Parameter(object):
    def __init__(self, interaction=10, learnrate=0.0008, lamda=0.005,\
        learndecay=0.96, k=4, rk=10):
        self.learnrate = learnrate
        self.interaction = interaction
        self.lamda = lamda
        self.learndecay = learndecay
        self.rk = rk
        self.k = k        
        
# Read data
class ReadDataMatrix(object):
    def __init__(self, url):
        self.url = url 
    
    def init_cooMatrix(self):
        ulist = []
        ilist = []
        vlist = []
        try:
            filer = open(self.url, 'r')
            for record in filer.readlines():
                message = record.split(',')
                uid = int(message[0])
                iid = int(message[1])
                ulist.append(uid)
                ilist.append(iid)
                vlist.append(1)
            print '{0}: Read Over.Path: {1}'.format(time.asctime(), self.url)
        except Exception, e:
            print '{0}: {1}'.format(time.asctime(), e)
        finally:
            coomatrix = sp.coo_matrix((vlist, (ulist, ilist)))
            print '{0}: Coo_matrix Ok.'.format(time.asctime())
        return coomatrix

# svd
class SVD(object):
    def __init__(self, pathurl):
        self.pathurl = pathurl
        self.urloflog = pathurl+'/log.txt'
        self.urlcriterion = pathurl+r'/evaluation_criterion.txt'
        self.filepathname = r'/svd{0}'.format(time.strftime('%Y.%m.%d_%H%M', time.localtime()))
        self.filepathurl = self.pathurl+self.filepathname
        if not os.path.exists(self.filepathurl):
            os.makedirs(self.filepathurl)
        self.filepathlog = self.filepathurl+'/log.txt'
        self.fileparameterurl = self.filepathurl+r'/parameter.npz'
        string = r'{0}: Begin.'.format(time.asctime())
        print string
        self.write_into_txt(self.urloflog, 'a', string)
        self.write_into_txt(self.filepathlog, 'a', string)
    
    def svd_initData(self, trainCoomatr, testCoomatr):
        self.trainDokmatri = trainCoomatr.todok()
        self.testDokmatri = testCoomatr.todok()
        string = r'{0}: Init Dokmatrix OK!'.format(time.asctime())
        print string
        self.write_into_txt(self.filepathlog, 'a', string)
    
    # write log  
    def write_into_txt(self, url, way, strline):
        filer = open(url, way)
        filer.writelines(strline+'\n')
        filer.close()

    def write_evaluate_criterion(self, url, evaluatelist):
        filer = open(url, 'a')
        string = ''
        length = len(evaluatelist)
        for i in xrange(length):
            if i == (length-1):
                string += str(evaluatelist[i])+'\n'
            else:
                string += str(evaluatelist[i])+','
        filer.writelines(string)
        filer.close()
    
    def svd_beginRecommendation(self, parameter):
        self.svd_configurate(parameter)
        self.svd_trainAdam(parameter)
        # self.svd_storeParameter()
        self.svd_recommendation(parameter)
        self.svd_test()
        self.svd_printparameter(parameter)
    
    def svd_printparameter(self, parameter):
        string = '====Experiment Parameter====' + \
        '\ninteraction= {0}, earnrate= {1}, lamda= {2}\n'\
        .format(parameter.interaction, parameter.learnrate, parameter.lamda) + \
        r'learndecay= {0}, k= {1}, rk= {2}'\
        .format(parameter.learndecay, parameter.k, parameter.rk)
        print string
        self.write_into_txt(self.filepathlog, 'a', string)
        
    def svd_configurate(self, parameter):
        self.U = (self.trainDokmatri.nnz+0.0) / \
            (self.trainDokmatri.shape[0]*self.trainDokmatri.shape[1])
        self.K = parameter.k
        self.evaluate_result = list()
        # insert into evaluate_result
        self.evaluate_result.append(self.filepathname)
        self.evaluate_result.append(self.K) 
        self.ItemNumber = self.trainDokmatri.shape[1]
        self.UserNumber = self.trainDokmatri.shape[0]
        self.bi = np.zeros((self.ItemNumber, 1))
        self.bu = np.zeros((self.UserNumber, 1))
        self.qi = np.random.random((self.ItemNumber, self.K))/(10*np.sqrt(self.K))
        self.pu = np.random.random((self.UserNumber, self.K))/(10*np.sqrt(self.K))
        string = r'{0}: Init OK!'.format(time.asctime())
        print string
        self.write_into_txt(self.filepathlog, 'a', string)
        string1 = '{0}: Configuration--\n U={1} K={2}\n TotalItemnumber={3} TotalUsernumber={4}'\
            .format(time.asctime(), self.U, self.K, self.ItemNumber, self.UserNumber)
        print string1
        self.write_into_txt(self.filepathlog, 'a', string1)
    
    def svd_predict(self, user, item):
        factorsum = self.U + self.bi[item, 0] + self.bu[user, 0] +\
            np.dot(self.pu[user], self.qi[item])
        return factorsum
    
    def svd_trainAdam(self, parameter):
        beginrmse = self.svd_rmse(self.trainDokmatri)
        string = r'{0}: Begin Rmse:{1}'.format(time.asctime(), beginrmse)
        print string
        self.write_into_txt(self.filepathlog, 'a', string)
        # set parameters
        learnrate = parameter.learnrate
        lamda = parameter.lamda
        interaction = parameter.interaction
        # insert into evaluate_result
        self.evaluate_result.append(interaction)
        learndecay = parameter.learndecay
        useritemtuple = self.trainDokmatri.keys()
        for inter in xrange(interaction):     
            # shuffle order
            np.random.shuffle(useritemtuple)
            for (user, item) in useritemtuple:
                rating = self.svd_predict(user, item)
                eui = 1.0 - rating
                ratefront = -eui
                g_bi = ratefront+lamda*self.bi[item]
                g_bu = ratefront+lamda*self.bu[user]
                g_qi = ratefront*self.pu[user]+lamda*self.qi[item]
                g_pu = ratefront*self.qi[item]+lamda*self.pu[user]
                self.bi[item] = self.bi[item]-learnrate*g_bi
                self.bu[item] = self.bu[item]-learnrate*g_bu
                self.qi[item] = self.qi[item]-learnrate*g_qi
                self.pu[item] = self.pu[item]-learnrate*g_pu
            learnrate *= learndecay
            srmse = self.svd_rmse(self.trainDokmatri)
            string5 = r'{0}: interaction:{1} Rmse:{2}'.format(time.asctime(), inter+1, srmse)
            print string5
            self.write_into_txt(self.filepathlog, 'a', string5)
        string2 = '{0}: Finish Adam train!\n'.format(time.asctime())
        print string2
        self.write_into_txt(self.filepathlog, 'a', string2)
    
    def svd_storeParameter(self):
        meanvalue = np.array([self.U])
        url = self.fileparameterurl
        np.savez(url, mean=meanvalue, bu=self.bu, bi=self.bi,
            pu=self.pu, qi=self.qi)

    def svd_rmse(self, dataDokmatri):
        # beginTime = time.clock()
        rmse = 0
        useritemtuple = dataDokmatri.keys()
        coupleNum = dataDokmatri.nnz
        for (user, item) in useritemtuple:
            rating = self.svd_predict(user, item)
            singleRmse = (1.0 - rating)**2
            rmse += singleRmse
        rmse = np.math.sqrt(rmse/coupleNum)
        # totaltime = time.clock() - beginTime
        # string = r'{0}: Time of RMSE: {1} s'.format(time.asctime(), totaltime)
        # print string
        # self.write_into_txt(self.filepathlog, 'a', string)
        return rmse
    
    def svd_recommendation(self, parameter):
        # recommendation result
        rk = parameter.rk
        begintime = time.clock()
        self.recommendationResultDict = dict()
        trainuserSet = set(self.trainDokmatri.tocoo().row)
        testuserSet = set(self.testDokmatri.tocoo().row)
        # train-test user intersection
        User_intersection = list(trainuserSet & testuserSet)
        endtime = time.clock() - begintime
        print r'{0}: User intersection Number: {1}'.format(time.asctime(), len(User_intersection))
        print r'{0}: Time of intersection: {1}'.format(time.asctime(), endtime)
        # transform
        tbegintime = time.clock()
        totalItem_buyList = self.trainDokmatri.tolil().rows
        tendtime = time.clock() - tbegintime
        print r'{0}: Time of transform: {1}'.format(time.asctime(), tendtime)
        # begin recommendation
        count = 0
        for user in User_intersection:
            item_havebuy = totalItem_buyList[user]
            count += 1
            if count % 50000 == 0:
                string2 = '{0}: Now recommend Number: {1}'.format(time.asctime(), count)
                print string2
                self.write_into_txt(self.filepathlog, 'a', string2)
            items_score = np.dot(self.qi, self.pu[user])+self.bi[:, 0]
            items_score_pair = zip(range(self.ItemNumber), items_score)
            items_score_pair.sort(key=lambda x: x[1], reverse=True)
            recomList = list()
            rknumber = 0
            for item in xrange(self.ItemNumber):
                if rknumber == rk:
                    break
                if item in item_havebuy:
                    continue
                else:
                    rknumber += 1
                    recomList.append(items_score_pair[item][0])
            self.recommendationResultDict.setdefault(user, recomList)
        string1 = '{0}: Recommendation OK! RK= {1}\n'.format(time.asctime(), rk)
        print string1
        self.write_into_txt(self.filepathlog, 'a', string1)
            
    def svd_test(self):
        recallsum = 0.0
        sharesum = 0.0
        predictsum = 0.0
        usersum = len(self.recommendationResultDict)
        totalItem_buyList = self.testDokmatri.tolil().rows
        for user in self.recommendationResultDict.keys():
            item_havebuy = totalItem_buyList[user]
            sharesum = len(set(self.recommendationResultDict[user]) & set(item_havebuy))+0.0
            # recallsum += sharesum/self.testDokmatri[user].nnz
            recallsum += sharesum/len(item_havebuy)
            predictsum += sharesum/len(self.recommendationResultDict[user])
        recall = recallsum/usersum
        string1 = '{0}:\n====Experiment Result====\nthe recall is: {1}'.format(time.asctime(), recall)
        self.write_into_txt(self.filepathlog, 'a', string1)
        print string1
        precision = predictsum/usersum
        string2 = 'the precision is: {0}'.format(precision)
        self.write_into_txt(self.filepathlog, 'a', string2)
        print string2
        f1 = 2*recall*precision/(recall+precision)
        string3 = 'the f1 is: {0}'.format(f1)
        self.write_into_txt(self.filepathlog, 'a', string3)
        print string3
        recommend_item, recommend_count = self.svd_itemstimes_statistic()
        coverage = (len(recommend_item)+0.0)/self.ItemNumber
        string4 = 'the coverage rate is: {0}'.format(coverage)
        self.write_into_txt(self.filepathlog, 'a', string4)
        print string4
        variety = self.svd_variety(recommend_item, recommend_count)
        string5 = 'the variety rate is: {0}'.format(variety)
        self.write_into_txt(self.filepathlog, 'a', string5)
        print string5
        # record result
        self.evaluate_result.append(recall)
        self.evaluate_result.append(precision)
        self.evaluate_result.append(f1)
        self.evaluate_result.append(coverage)
        self.evaluate_result.append(variety)
        self.write_evaluate_criterion(self.urlcriterion, self.evaluate_result)
    
    def svd_itemstimes_statistic(self):
        # recommend  {item:times}
        recommend_result_times = dict()
        count = 0
        for user in self.recommendationResultDict.keys():
            for item in self.recommendationResultDict[user]:
                count += 1
                if recommend_result_times.has_key(item):
                    recommend_result_times[item] += 1
                else:
                    recommend_result_times.setdefault(item, 1)
        recommend_result_alltimes = count
        return recommend_result_times, recommend_result_alltimes

    def svd_variety(self, recommend_result_times, recommend_result_alltimes):
        varietysum = 0.0
        h = 0
        log = np.log
        alltime = recommend_result_alltimes
        for item in recommend_result_times:
            times = (recommend_result_times[item]+0.0)/alltime
            h = -times*log(times)
            varietysum += h
        return varietysum
      

def main():
    string = '------------------------------------\
    \n{0}: Process begin.'.format(time.asctime())
    print string
    thisFile = inspect.getfile(inspect.currentframe())
    paths = os.path.abspath(os.path.dirname(thisFile))
    parentpath = os.path.dirname(paths)
    urluabase = r'{0}/train_data.csv'.format(paths)
    urluatest = r'{0}/test_data.csv'.format(paths)
    urlpath = r'{0}/svd'.format(parentpath)
    if not os.path.exists(urlpath):
        os.makedirs(urlpath)
    trainCoomtr = ReadDataMatrix(urluabase).init_cooMatrix()
    testCoomtr = ReadDataMatrix(urluatest).init_cooMatrix()
    parameter = Parameter(interaction=1, learnrate=0.0001, lamda=0.1,\
        learndecay=0.96, k=4, rk=10)
    svd = SVD(urlpath)
    svd.svd_initData(trainCoomtr, testCoomtr)
    svd.svd_beginRecommendation(parameter=parameter)
    
    
if __name__ == '__main__':
    main()