from KMM.model import Model


def readFiles(EMB, LBL):
    traindata = []
    with open(EMB) as fileEmb, open(LBL) as fileLbl: 
        for Emb, lbl in zip(fileEmb, fileLbl):
            
            data = map(lambda x: float(x), Emb.split(',')) 
            lb = int(lbl)
            x = {-1:lb}
            
            for i, d in zip( xrange(300), data):
                x[i] = d
    
            #print x
            traindata.append(x)
    return traindata


if __name__ == '__main__':
    
    traindata = readFiles('features1.txt', 'Label1.txt')
    testdata = readFiles('features2.txt', 'Label2.txt')
    
    
    
    labels = [0, 1]
    maxvar = 300
    model = Model()
    model.train(traindata,testdata, maxvar)
    result = model.test(testdata, maxvar)
    
    
    TP = 0
    FN = 0
    FP = 0
    TN=0
    correct = 0
    incorrect = 0
    
    with open('Label2.txt') as fileTeLbl:
        for PreLbl, TrueLbl in zip(result, fileTeLbl):
            if PreLbl[0] == float(TrueLbl): 
                correct +=1
                if int(TrueLbl) == 1: 
                    TP +=1
                else:
                    TN +=1
            elif PreLbl[2] == 0:
                FP +=1
            elif PreLbl[2] == 1:
                FN +=1
            if PreLbl[0] != int(TrueLbl): 
                incorrect +=1
    
    
    print TP, FP, FN, TN
    
    accuracy = float(correct)/ len(result)
    recall = float (TP) / (TP + FN)
    precision = float (TP) / (TP + FP)
    
    print accuracy *100
    print precision *100
    print recall*100
    print 100* (2*precision* recall)/(precision+recall)

