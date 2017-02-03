# eval.py ../featureextraction/nytimes.postfeats.norm.out.5 "lrm" ../featureextraction/predictions_for_test.out.5

# This script assumes that the ground truth labels are in the featurefile (also for the oracle ranking)

import operator
import sys
import re
import numpy

featurefile = sys.argv[1]
methodname = sys.argv[2]
predictionsfile = sys.argv[3]


models = dict()
models[methodname] = 1

def get_selected_from_featurefile(featurefile):
    feat = open(featurefile)
    threadids = []
    postids = []
    selecteds = []
    for line in feat:
        columns = line.rstrip().split("\t")
        selected = columns[-1]
        threadid = columns[0]
        postid = columns[1]

        if re.match("[0-9.-]+",selected):
            selecteds.append(selected)
            threadids.append(threadid)
            postids.append(postid)
            #print(threadid,postid,selected)
    return threadids,postids,selecteds

def get_oracle_ranking(featurefile):
    array_of_threadids, array_of_postids, array_of_selecteds = get_selected_from_featurefile(featurefile)
    for i in range(0,len(array_of_threadids)):

        threadid = array_of_threadids[i]
        postid = array_of_postids[i]
        selected = array_of_selecteds[i]

        selected_for_this_thread = dict()
        if threadid in selected_per_thread:
            selected_for_this_thread = selected_per_thread[threadid]
        selected_for_this_thread[postid] = selected
        selected_per_thread[threadid] = selected_for_this_thread

    ranked_postids_per_thread = dict()
    for threadid in selected_per_thread:
        selected_for_this_thread = selected_per_thread[threadid]
        ranked_postids_with_score = sorted(selected_for_this_thread.items(), key=operator.itemgetter(1),reverse=True)

        ranked_postids = []
        for (postid,score) in ranked_postids_with_score:
            ranked_postids.append(postid)
            print ("oracle:",predictions_per_thread[threadid],selected_per_thread[threadid])
        ranked_postids_per_thread[threadid] = ranked_postids
    return ranked_postids_per_thread

def get_predictions_from_predictionsfile(predictionsfile):
    pred = open(predictionsfile)
    predictions = []
    for line in pred:
        prediction = line.rstrip()
        if re.match("[0-9.-]+",prediction):
            predictions.append(float(prediction))
            #print (prediction)
    return predictions


def compute_jaccard_index(set_1, set_2):
    if len(set_1)+len(set_2)>0:
        n = len(set_1.intersection(set_2))
        return n / float(len(set_1) + len(set_2) - n)
    else:
        return 1

def compute_precision(model,reference):
    if len(model)+len(reference)>0:
        tp=len(model.intersection(reference))
        fp=len(model-reference)
        if tp > 0:
            return float(tp)/(float(fp)+float(tp))
        else:
            return 0
    else:
        return 1

def compute_recall(model,reference):
    if len(model)+len(reference)>0:
        tp=len(model.intersection(reference))
        fn=len(reference-model)
        if tp > 0:
            return float(tp)/(float(fn)+float(tp))
        else:
            return 0
    else:
        return 1

def compute_kappa(list1,list2):
    if not len(list1) == len(list2):
        print ("Error: lists not same length: ", list1, list2)
    elif numpy.sum(list1)+numpy.sum(list2)>0:
        E1 = float(numpy.sum(list1))/float(len(list1)) * float(numpy.sum(list2))/float(len(list2))  #sum is the number of 1s
        E0 = float((len(list1)-numpy.sum(list1)))/float(len(list1)) * float((len(list2)-numpy.sum(list2)))/float(len(list2))    # len - sum is the number of 0s
        ExpAgr = E1+E0
        count_agreed = 0
        for j in range(0,len(list1)-1):
            if not list1[j]+list2[j] == 1:
                # agreed if sum is 2 or 0
                count_agreed += 1
        MeasAgr = float(count_agreed)/float(len(list1))
        #print E1, E0, ExpAgr, MeasAgr
        k = (MeasAgr-ExpAgr)/(1-ExpAgr)
        return k
    else:
        return 1


def print_evaluation(ranked_postids_per_thread,method,true_set):
    for cutoff in range (1,20):

        selected_set_by_model = set()
        for threadid in ranked_postids_per_thread:
            ranked_postids = ranked_postids_per_thread[threadid]
            #print (threadid,ranked_postids)
            selectedposts = dict()
            k=0
            for postid in ranked_postids:
                k +=1
                if k <= cutoff:
                    selectedposts[postid] = 1
                    selected_item = threadid+"_"+postid
                    selected_set_by_model.add(selected_item)

        #print ("selected:",selected_set_by_model)
        #print ("true_set:",true_set)
        precision = compute_precision(selected_set_by_model,true_set)
        recall = compute_recall(selected_set_by_model,true_set)
        #print (method,"\t",cutoff,"\t",recall, "\t", precision)
        f1 = 2*(precision*recall)/(precision+recall)
        print (method,"\t",cutoff,"\t",recall, "\t", precision, "\t", f1)

'''
MAIN
'''




#print (models)
#print (usernames)

for method in models:
    print ("METHOD:",method)


    array_of_threadids, array_of_postids, array_of_selecteds = get_selected_from_featurefile(featurefile)
    array_of_predictions = get_predictions_from_predictionsfile(predictionsfile)

    predictions_per_thread = dict()
    selected_per_thread = dict()
    true_set = set()
    for i in range(0,len(array_of_threadids)):

        threadid = array_of_threadids[i]
        postid = array_of_postids[i]
        selected = array_of_selecteds[i]
        predicted = array_of_predictions[i]
        #print (i,threadid,postid,selected,predicted)

        predictions_for_this_thread = dict()
        if threadid in predictions_per_thread:
            predictions_for_this_thread = predictions_per_thread[threadid]
        predictions_for_this_thread[postid] = predicted
        predictions_per_thread[threadid] = predictions_for_this_thread

        #selected_for_this_thread = dict()
        #if threadid in selected_per_thread:
        #    selected_for_this_thread = selected_per_thread[threadid]
        #selected_for_this_thread[postid] = selected
        #selected_per_thread[threadid] = selected_for_this_thread
        if selected == "1":
            selected_item = threadid+"_"+postid
            true_set.add(selected_item)

    ranked_postids_per_thread = dict()
    for threadid in predictions_per_thread:
        predictions_for_this_thread = predictions_per_thread[threadid]
        ranked_postids_with_score = sorted(predictions_for_this_thread.items(), key=operator.itemgetter(1),reverse=True)

        ranked_postids = []
        for (postid,score) in ranked_postids_with_score:
            ranked_postids.append(postid)
        #   print (predictions_per_thread[threadid],selected_per_thread[threadid])
        ranked_postids_per_thread[threadid] = ranked_postids
        #print (threadid,ranked_postids)

    print_evaluation(ranked_postids_per_thread,method,true_set)


ranked_postids_per_thread_oracle = get_oracle_ranking(featurefile)
print_evaluation(ranked_postids_per_thread_oracle,"oracle",true_set)